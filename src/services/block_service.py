import json
import os
from loguru import logger
from src.bot.config import DATA_FOLDER

BLOCKED_FILE = os.path.join(DATA_FOLDER, 'blocked.json')

class BlockService:
    """
    Service for managing blocked users.
    Implements a singleton pattern.
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

    def is_blocked(self, user_id: int) -> bool:
        """
        Checks if a user is blocked.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            bool: True if the user is blocked; otherwise, False.
        """
        return user_id in self.blocked

    def block_user(self, user_id: int) -> None:
        """
        Blocks a user by adding their ID to the blocked list and updating Redis if available.

        Args:
            user_id (int): The Telegram user ID to block.
        """
        if user_id not in self.blocked:
            self.blocked.append(user_id)
            self._write_blocked(self.blocked)
            if self.redis_service and self.redis_service.client:
                # Convert boolean to a string before saving to Redis
                self.redis_service.client.set(f"blocked:{user_id}", "True")
            logger.info(f"User {user_id} blocked")

    def unblock_user(self, user_id: int) -> None:
        """
        Unblocks a user by removing their ID from the blocked list and updating Redis if available.

        Args:
            user_id (int): The Telegram user ID to unblock.
        """
        if user_id in self.blocked:
            self.blocked.remove(user_id)
            self._write_blocked(self.blocked)
            if self.redis_service and self.redis_service.client:
                self.redis_service.client.delete(f"blocked:{user_id}")
            logger.info(f"User {user_id} unblocked")
