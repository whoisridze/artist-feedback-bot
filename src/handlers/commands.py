from loguru import logger
from telebot import TeleBot
from src.bot.config import load_config
from src.services.block_service import BlockService

def register_command_handlers(bot: TeleBot):
    """
    Registers command handlers for the bot.
    
    Args:
        bot (TeleBot): The Telegram bot instance.
    """
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(command):
        """
        Sends a welcome message in response to /start and /help commands.
        
        Args:
            command: The command message received from the user.
        """
        text = "Hello! Feel free to send your feedback or questions here. I will try to respond as soon as possible."
        logger.info(f"Received command: {command.text} from user {command.from_user.id}")
        bot.reply_to(command, text)

    @bot.message_handler(commands=['block'])
    def block_command(message):
        """
        Blocks a user based on the provided identifier.
        Only the admin (recipient_id) can use this command.
        
        Usage: /block <identifier>
        Where identifier is either the username (with or without @) or the numeric ID.
        """
        config = load_config()
        if message.from_user.id != config.recipient_id:
            bot.reply_to(message, "You are not authorized to use this command.")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /block <identifier>")
            return
        identifier = parts[1]
        # Normalize identifier: remove "@" if present
        if identifier.startswith('@'):
            identifier = identifier[1:]
        block_service = BlockService()
        if block_service.block_user(identifier):
            bot.reply_to(message, f"User {identifier} has been blocked.")
        else:
            bot.reply_to(message, f"User {identifier} is already blocked.")

    @bot.message_handler(commands=['unblock'])
    def unblock_command(message):
        """
        Unblocks a user based on the provided identifier.
        Only the admin (recipient_id) can use this command.
        
        Usage: /unblock <identifier>
        Where identifier is either the username (with or without @) or the numeric ID.
        """
        config = load_config()
        if message.from_user.id != config.recipient_id:
            bot.reply_to(message, "You are not authorized to use this command.")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /unblock <identifier>")
            return
        identifier = parts[1]
        if identifier.startswith('@'):
            identifier = identifier[1:]
        block_service = BlockService()
        if block_service.unblock_user(identifier):
            bot.reply_to(message, f"User {identifier} has been unblocked.")
        else:
            bot.reply_to(message, f"User {identifier} is not blocked.")
