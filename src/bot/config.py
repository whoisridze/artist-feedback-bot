import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get config from environment variables
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    recipient_id = os.getenv("RECIPIENT_ID")
    
    # Validate config
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN is missing in environment variables")
    if not recipient_id:
        raise ValueError("RECIPIENT_ID is missing in environment variables")
    
    return {
        "TELEGRAM_TOKEN": telegram_token,
        "RECIPIENT_ID": recipient_id,
    }

# Constants for file paths
DATA_FOLDER = os.path.join('src', 'data')
FEEDBACK_FILE = os.path.join(DATA_FOLDER, 'feedback.json')