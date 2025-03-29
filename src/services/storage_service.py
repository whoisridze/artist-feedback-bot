import json
import os
from typing import Dict, Any
from loguru import logger
from src.bot.config import DATA_FOLDER, FEEDBACK_FILE

class StorageService:
    def __init__(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)
        self.data = self._read_file()
        
    def _read_file(self) -> Dict[str, Any]:
        if not os.path.exists(FEEDBACK_FILE):
            self._write_to_file({"number_of_messages": 0})
            
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.loads(f.read())
                logger.debug('Content loaded from json')
            except json.JSONDecodeError:
                logger.warning('Feedback file is empty, initializing...')
                self._write_to_file({"number_of_messages": 0})
                data = self._read_file()

        return data
    
    def _write_to_file(self, data: Dict[str, Any]) -> None:
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            logger.debug('Content written to json')
    
    def add_message(self, message_text: str, date: str, time: str) -> Dict[str, Any]:
        self.data['number_of_messages'] += 1
        
        self.data[str(self.data['number_of_messages'])] = {
            'date': date,
            'time': time,
            'text': message_text
        }
        
        self._write_to_file(self.data)
        return self.data