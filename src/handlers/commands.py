from loguru import logger

def register_command_handlers(bot):
    """Register command handlers with the bot"""
    
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(command):
        text = """Hello! Feel free to send your feedback or questions here. I will try to respond as soon as possible."""

        logger.info(f'Received command: {command.text} from user {command.from_user.id}')
        bot.reply_to(command, text)