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
        Blocks a user based on their user ID. Only the admin (recipient_id) can use this command.

        Usage: /block <userid>
        """
        config = load_config()
        if message.from_user.id != config.recipient_id:
            bot.reply_to(message, "You are not authorized to use this command.")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /block <userid>")
            return
        try:
            userid = int(parts[1])
        except ValueError:
            bot.reply_to(message, "User ID must be a number.")
            return
        block_service = BlockService()
        block_service.block_user(userid)
        bot.reply_to(message, f"User {userid} has been blocked.")

    @bot.message_handler(commands=['unblock'])
    def unblock_command(message):
        """
        Unblocks a user based on their user ID. Only the admin (recipient_id) can use this command.

        Usage: /unblock <userid>
        """
        config = load_config()
        if message.from_user.id != config.recipient_id:
            bot.reply_to(message, "You are not authorized to use this command.")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /unblock <userid>")
            return
        try:
            userid = int(parts[1])
        except ValueError:
            bot.reply_to(message, "User ID must be a number.")
            return
        block_service = BlockService()
        block_service.unblock_user(userid)
        bot.reply_to(message, f"User {userid} has been unblocked.")
