import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class RedisConfig:
    host: str
    port: int
    username: str
    password: str
    decode_responses: bool = True

@dataclass
class Config:
    telegram_token: str
    recipient_id: int
    redis: RedisConfig

DATA_FOLDER = os.path.join('src', 'data')
FEEDBACK_FILE = os.path.join(DATA_FOLDER, 'feedback.json')

def load_config() -> Config:
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    recipient_id = os.getenv("RECIPIENT_ID")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_username = os.getenv("REDIS_USERNAME", "default")
    redis_password = os.getenv("REDIS_PASSWORD")
    
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN is missing")
    if not recipient_id:
        raise ValueError("RECIPIENT_ID is missing")
    if not all([redis_host, redis_port, redis_password]):
        raise ValueError("Redis configuration is incomplete")
    
    return Config(
        telegram_token=telegram_token,
        recipient_id=int(recipient_id),
        redis=RedisConfig(
            host=redis_host,
            port=int(redis_port),
            username=redis_username,
            password=redis_password
        )
    )