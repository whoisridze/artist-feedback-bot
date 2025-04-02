from typing import Optional, Tuple
import redis
from loguru import logger
from src.bot.config import RedisConfig

class RedisService:
    """
    Service for managing Redis connection and rate limiting.
    """
    _instance = None
    
    def __new__(cls, config: Optional[RedisConfig] = None):
        """
        Implements the singleton pattern to ensure only one Redis connection exists.
        
        Args:
            config (Optional[RedisConfig]): Redis configuration parameters.
            
        Returns:
            RedisService: An instance of RedisService.
        """
        if cls._instance is None and config is not None:
            cls._instance = super(RedisService, cls).__new__(cls)
            cls._instance._initialize(config)
        return cls._instance
    
    def _initialize(self, config: RedisConfig):
        """
        Initializes the Redis client with the given configuration.
        
        Args:
            config (RedisConfig): The Redis configuration.
        """
        try:
            self.client = redis.Redis(
                host=config.host,
                port=config.port,
                username=config.username,
                password=config.password,
                decode_responses=config.decode_responses
            )
            self.client.ping()
            logger.info("Connected to Redis successfully")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def check_rate_limit(self, user_id: int, limit_type: str) -> Tuple[bool, int]:
        """
        Checks whether a user has exceeded the allowed rate limit.

        Args:
            user_id (int): The user's Telegram ID.
            limit_type (str): The type of rate limit to check ('fast' or 'slow').

        Returns:
            Tuple[bool, int]: A tuple where the first element indicates if the rate limit is exceeded,
                              and the second element is the remaining time to wait if exceeded.
        """
        if not self.client:
            return False, 0
            
        try:
            if limit_type == 'fast':
                key, window, max_requests = f"rate:fast:{user_id}", 2, 2
            else:
                key, window, max_requests = f"rate:slow:{user_id}", 60, 3
                
            current = self.client.get(key)
            
            if current is None:
                self.client.set(key, 1, ex=window)
                return False, 0
                
            current = int(current)
            
            if current >= max_requests:
                ttl = self.client.ttl(key)
                return True, ttl
                
            self.client.incr(key)
            return False, 0
            
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            return False, 0
