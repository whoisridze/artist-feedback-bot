import telebot
from src.bot.config import load_config
from src.bot.storage import read_file
from src.handlers.commands import register_command_handlers
from src.handlers.messages import register_message_handlers
from src.handlers.callbacks import register_callback_handlers
from src.bot.logger import setup_logger

# Initialize logger
logger = setup_logger()

def main():
    """Entry point for the bot application"""
    # Load configuration
    config = load_config()
    telegram_token = config["TELEGRAM_TOKEN"]
    recipient_id = config["RECIPIENT_ID"]
    redis_config = config.get("REDIS")
    
    # Initialize bot
    bot = telebot.TeleBot(telegram_token, parse_mode=None)
    
    # Load data
    file_data = read_file()
    
    # Register handlers
    register_command_handlers(bot)
    register_message_handlers(bot, file_data, recipient_id, redis_config)
    register_callback_handlers(bot)
    
    # Start bot
    logger.info('Bot is now running')
    bot.infinity_polling(timeout=5)

if __name__ == '__main__':
    main()