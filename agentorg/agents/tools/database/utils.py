import sqlite3
from typing import Optional
from datetime import datetime, date, time
import uuid
import logging

from langchain_core.runnables.config import RunnableConfig
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agentorg.utils.utils import chunk_string
from agentorg.utils.model_config import MODEL
from agentorg.utils.graph_state import Slot, MessageState
from agentorg.agents.prompts import database_slot_prompt
from agentorg.utils.graph_state import StatusEnum


DB_PATH = 'show_booking_db.sqlite'

logger = logging.getLogger(__name__)


user_id = "user_be6e1836-8fe9-4938-b2d0-48f810648e72"


SLOTS = [
    {
        "name": "show_name",
        "slot_type": "string",
        "description": "Name of the show",
        "slot_values": {
            "original_value": "Carmen", 
            "verified_value": None, 
            "prompt": None
        },
        "confirmed": False
    },
    {
        "name": "location",
        "slot_type": "string",
        "description": "Location of the show",
        "slot_values": {
            "original_value": "New York", 
            "verified_value": None, 
            "prompt": None
        },
        "confirmed": False
    },
    {
        "name": "date",
        "slot_type": "date",
        "description": "Date of the show",
        "slot_values": {
            "original_value": "2022-12-31", 
            "verified_value": None, 
            "prompt": None
        },
        "confirmed": False
    },
    {
        "name": "time",
        "slot_type": "time",
        "description": "Time of the show",
        "slot_values": {
            "original_value": "19:00", 
            "verified_value": None, 
            "prompt": None
        },
        "confirmed": False
    }
]


class DatabaseActions:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.slots = []

    def init_slots(self, slots: list[Slot]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for slot in slots:
            query = f"SELECT DISTINCT {slot['name']} FROM show"
            cursor.execute(query)
            results = cursor.fetchall()
            value_list = [result[0] for result in results]
            self.slots.append(self.verify_slot(slot, value_list))
        cursor.close()
        conn.close()

    def verify_slot(self, slot: Slot, value_list: list) -> Slot:
        if slot["confirmed"]:
            logger.info(f"Slot {slot['name']} already confirmed")
            return slot
        if slot["slot_values"]["original_value"] is None:
            logger.info(f"Slot {slot['name']} has no original value")
            return slot
        prompt = PromptTemplate.from_template(database_slot_prompt)
        input_prompt = prompt.invoke({
            "slot": {"name": slot["name"], "description": slot["description"], "slot_type": slot["slot_type"]}, 
            "value": slot["slot_values"]["original_value"], 
            "value_list": value_list
        })
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        logger.info(f"Chunked prompt for verifying slot: {chunked_prompt}")
        final_chain = self.llm | StrOutputParser()
        try:
            answer = final_chain.invoke(chunked_prompt)
            for value in value_list:
                if value in answer:
                    logger.info(f"Chosen slot value in the database agent: {value}")
                    slot["slot_values"]["verified_value"] = value
                    slot["confirmed"] = True
                    return slot
        except Exception as e:
            logger.error(f"Error occurred while verifying slot in the database agent: {e}")
        return slot

    def search_show(self, msg_state: MessageState) -> MessageState:
        slot_list = msg_state["slots"]
        # Populate the slots with verified values
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM show WHERE 1 = 1"
        params = []
        for slot in slot_list:
            if slot["confirmed"]:
                query += f" AND {slot['name']} = ?"
                params.append(slot["slot_values"]["verified_value"])
        # Execute the query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()
        msg_state["status"] = StatusEnum.COMPLETE
        return results


    def book_show(self, config: RunnableConfig, msg_state: MessageState):
        user_id = config.get("user_id", None)
        if not user_id:
            raise ValueError("No user ID configured.")
        slot_list = msg_state["slots"]
        # Populate the slots with verified values
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM show WHERE 1 = 1"
        params = []
        for slot in slot_list:
            if slot["confirmed"]:
                query += f" AND {slot['name']} = ?"
                params.append(slot["slot_values"]["verified_value"])
        # Execute the query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        # Check whether info is enough to book a show
        if len(rows) == 0:
            cursor.close()
            conn.close()
            msg_state["status"] = StatusEnum.INCOMPLETE
            return "Show is not found."
        elif len(rows) > 1:
            cursor.close()
            conn.close()
            msg_state["status"] = StatusEnum.INCOMPLETE
            return "Multiple shows found."
        row = rows[0]
        show_id = row["id"]
        column_names = [column[0] for column in cursor.description]
        result = dict(zip(column_names, row))

        # Insert a row into the booking table
        cursor.execute('''
            INSERT INTO booking (id, show_id, user_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', ("booking_" + str(uuid.uuid4()),  show_id, user_id, datetime.now()))

        cursor.close()
        conn.close()
        msg_state["status"] = StatusEnum.COMPLETE
        return result


    def check_booking(self, config: RunnableConfig):
        user_id = config.get("user_id", None)
        if not user_id:
            raise ValueError("No user ID configured.")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT * FROM
            booking b
            JOIN show s ON b.show_id = s.id
        WHERE
            b.user_id = ?
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results


    def cancel_booking(self, config: RunnableConfig):
        booked_shows = self.check_booking(config)
        if not booked_shows:
            raise ValueError("No shows booked.")
        elif len(booked_shows) > 1:
            raise ValueError("Multiple shows booked. Please provide more details.")
        show = booked_shows[0]

        connection = sqlite3.connect("your_database.db")
        cursor = connection.cursor()

        # Delete a row from the booking table based on show_id
        cursor.execute('''DELETE FROM booking WHERE show_id = ?
        ''', (show["id"],))

        connection.commit()
        connection.close()

        return show


dbf = DatabaseFunctions()
print(dbf.search_show("Carmen"))