import os
from typing import Dict
import requests
import logging

logger = logging.getLogger(__name__)


class NLU:
    def __init__(self, url):
        self.url = url

    def execute(self, text:str, intents:dict, chat_history_str:str):
        print(f"intents in {self.__class__.__name__}: {intents}")
        data = {
            "text": text,
            "intents": intents,
            "chat_history_str": chat_history_str
        }
        response = requests.post(self.url, json=data)

        if response.status_code == 200:
            results = response.json()
            pred_intent = results['intent']
            print(f"pred_intent is {pred_intent}")
        else:
            pred_intent = "others"
            print('Remote Server Error when predicting NLU')

        
        return pred_intent
