import sqlite3
from typing import Optional
from datetime import datetime, date, time
import uuid

from langchain_core.runnables.config import RunnableConfig


DB_PATH = 'show_booking_db.sqlite'


user_id = "user_be6e1836-8fe9-4938-b2d0-48f810648e72"


class DatabaseFunctions:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path


    def search_show(self, name: Optional[str] = None, genre: Optional[str] = None, date: Optional[date] = None, time: Optional[time] = None, location: Optional[str] = None, price: Optional[float] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM show WHERE 1 = 1"
        params = []

        if name:
            query += " AND name = ?"
            params.append(name)

        if genre:
            query += " AND genre = ?"
            params.append(genre)

        if date:
            query += " AND date = ?"
            params.append(date)

        if time:
            query += " AND time = ?"
            params.append(time)

        if location:
            query += " AND location = ?"
            params.append(location)

        if price:
            query += " AND price = ?"
            params.append(price)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results


    def book_show(self, config: RunnableConfig, name: str, date: Optional[date], time: Optional[time], location: Optional[str]):
        user_id = config.get("user_id", None)
        if not user_id:
            raise ValueError("No user ID configured.")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM show WHERE name = ?"
        params = [name]

        if date:
            query += " AND date = ?"
            params.append(date)
        
        if time:
            query += " AND time = ?"
            params.append(time)
        
        if location:
            query += " AND location = ?"
            params.append(location)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        if len(rows) == 0:
            raise ValueError("Show not found.")
        elif len(rows) > 1:
            raise ValueError("Multiple shows found. Please provide more details.")
        
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

        return result


    def check_booking(self, config: RunnableConfig = None):
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