import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get config from environment variables
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    recipient_id = os.getenv("RECIPIENT_ID")
    
    # Get Redis configuration
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_username = os.getenv("REDIS_USERNAME", "default")
    redis_password = os.getenv("REDIS_PASSWORD")
    
    # Validate config
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN is missing in environment variables")
    if not recipient_id:
        raise ValueError("RECIPIENT_ID is missing in environment variables")
    if not all([redis_host, redis_port, redis_password]):
        raise ValueError("Redis configuration is incomplete in environment variables")
    
    return {
        "TELEGRAM_TOKEN": telegram_token,
        "RECIPIENT_ID": recipient_id,
        "REDIS": {
            "host": redis_host,
            "port": int(redis_port),
            "username": redis_username,
            "password": redis_password,
            "decode_responses": True
        }
    }

# Constants for file paths
DATA_FOLDER = os.path.join('src', 'data')
FEEDBACK_FILE = os.path.join(DATA_FOLDER, 'feedback.json')