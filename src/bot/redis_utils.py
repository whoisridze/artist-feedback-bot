import redis
from loguru import logger
from functools import wraps

# Redis connection instance
_redis_client = None

def get_redis_client(config):
    """Get or create Redis client instance"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(**config)
            # Test connection
            _redis_client.ping()
            logger.info("Connected to Redis successfully")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            _redis_client = None
    return _redis_client

def check_rate_limit(user_id, limit_type):
    """Check if user has exceeded rate limits
    
    Args:
        user_id: The Telegram user ID
        limit_type: 'fast' or 'slow'
        
    Returns:
        tuple: (is_limited, seconds_to_wait)
    """
    if not _redis_client:
        logger.warning("Redis not available, skipping rate limiting")
        return False, 0
        
    try:
        now = _redis_client.time()[0]  # Get Redis server time
        
        if limit_type == 'fast':
            # Fast rate: 2 messages in 2 seconds
            key = f"rate:fast:{user_id}"
            window = 2  # seconds
            max_requests = 2
        else:
            # Slow rate: 3 messages in 60 seconds
            key = f"rate:slow:{user_id}"
            window = 60  # seconds
            max_requests = 3
            
        # Get current count for this window
        current = _redis_client.get(key)
        
        if current is None:
            # First request in this window
            _redis_client.set(key, 1, ex=window)
            return False, 0
            
        current = int(current)
        
        if current >= max_requests:
            # Rate limit exceeded
            ttl = _redis_client.ttl(key)
            return True, ttl
            
        # Increment and return
        _redis_client.incr(key)
        return False, 0
        
    except redis.RedisError as e:
        logger.error(f"Redis error in rate limiting: {e}")
        return False, 0  # On error, don't rate limit 