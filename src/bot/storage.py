import json
import os
from src.bot.config import DATA_FOLDER, FEEDBACK_FILE
from loguru import logger

# Ensure data directory exists
os.makedirs(DATA_FOLDER, exist_ok=True)

def read_file():
    """Read feedback data from JSON file"""
    if not os.path.exists(FEEDBACK_FILE):
        write_to_file({"number_of_messages": 0})
        
    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.loads(f.read())
            logger.debug('Content loaded from json')
        except json.JSONDecodeError:
            logger.warning('Feedback file is empty, initializing...')
            write_to_file({"number_of_messages": 0})
            data = read_file()

    return data

def write_to_file(data):
    """Write feedback data to JSON file"""
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        logger.debug('Content written to json')

def add_message(file_data, message_text, date, time):
    """Add a new message to the feedback data"""
    file_data['number_of_messages'] += 1
    
    file_data[str(file_data['number_of_messages'])] = {
        'date': date,
        'time': time,
        'text': message_text
    }
    
    write_to_file(file_data)
    return file_data