import telebot
from src.bot.config import load_config
from src.services.logger_service import setup_logger
from src.services.redis_service import RedisService
from src.services.storage_service import StorageService
from src.handlers.commands import register_command_handlers
from src.handlers.messages import register_message_handlers
from src.handlers.callbacks import register_callback_handlers

logger = setup_logger()

def main():
    # Load configuration and initialize services
    config = load_config()
    storage_service = StorageService()
    redis_service = RedisService(config.redis)
    
    # Initialize bot
    bot = telebot.TeleBot(config.telegram_token)
    
    # Register handlers
    register_command_handlers(bot)
    register_message_handlers(bot, storage_service, config.recipient_id, redis_service)
    register_callback_handlers(bot)
    
    # Start bot
    logger.info('Bot is now running')
    bot.infinity_polling(timeout=5)

if __name__ == '__main__':
    main()