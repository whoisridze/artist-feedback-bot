import json
import os
from loguru import logger
from src.bot.config import DATA_FOLDER

BLOCKED_FILE = os.path.join(DATA_FOLDER, 'blocked.json')

class BlockService:
    """
    Service for managing blocked users.
    Implements a singleton pattern.
    Stores the identifier (username if available, otherwise user ID as a string).
    """
    _instance = None

    def __new__(cls, redis_service=None):
        if cls._instance is None:
            cls._instance = super(BlockService, cls).__new__(cls)
            cls._instance.redis_service = redis_service
            cls._instance._init_file()
            cls._instance.blocked = cls._instance._read_blocked()
        return cls._instance

    def _init_file(self):
        if not os.path.exists(BLOCKED_FILE):
            self._write_blocked([])

    def _read_blocked(self):
        try:
            with open(BLOCKED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error reading blocked file: {e}")
            return []

    def _write_blocked(self, data):
        try:
            with open(BLOCKED_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error writing blocked file: {e}")

    def is_blocked(self, user_identifier: str) -> bool:
        """
        Checks if a user is blocked based on the identifier.
        
        Args:
            user_identifier (str): The user's username (without '@') or their ID as string.
            
        Returns:
            bool: True if the user is blocked; otherwise, False.
        """
        return user_identifier in self.blocked

    def block_user(self, user_identifier: str) -> bool:
        """
        Blocks a user by adding their identifier to the blocked list and updating Redis if available.
        
        Args:
            user_identifier (str): The user's username (without '@') or their ID as string.
        
        Returns:
            bool: True if the user was blocked; False if they were already blocked.
        """
        if user_identifier in self.blocked:
            logger.info(f"User {user_identifier} is already blocked")
            return False
        self.blocked.append(user_identifier)
        self._write_blocked(self.blocked)
        if self.redis_service and self.redis_service.client:
            self.redis_service.client.set(f"blocked:{user_identifier}", "True")
        logger.info(f"User {user_identifier} blocked")
        return True

    def unblock_user(self, user_identifier: str) -> bool:
        """
        Unblocks a user by removing their identifier from the blocked list and updating Redis if available.
        
        Args:
            user_identifier (str): The user's username (without '@') or their ID as string.
        
        Returns:
            bool: True if the user was unblocked; False if they were not blocked.
        """
        if user_identifier not in self.blocked:
            logger.info(f"User {user_identifier} is not blocked")
            return False
        self.blocked.remove(user_identifier)
        self._write_blocked(self.blocked)
        if self.redis_service and self.redis_service.client:
            self.redis_service.client.delete(f"blocked:{user_identifier}")
        logger.info(f"User {user_identifier} unblocked")
        return True
