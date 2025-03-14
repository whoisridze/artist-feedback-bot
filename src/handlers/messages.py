import datetime as dt
import json
from telebot import types
from src.bot import storage
from loguru import logger

def register_message_handlers(bot, file_data, recipient_id):
    """Register message handlers with the bot"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        if not any(c.isalnum() for c in message.text):
            logger.warning(f'User {message.from_user.id} tried to send emoji-only message')
            bot.reply_to(message, 'Please include some text in your message, not just emojis.')
            return

        if len(message.text) > 500:
            logger.warning(f'User {message.from_user.id} tried to send message exceeding 500 chars')
            bot.reply_to(message,
                        'Sorry, your message is too long. Please divide it into several parts and try again.')
            return

        answer = f"""Thank you! Your message: "{message.text}"
Has been successfully recorded. You'll receive a response soon.✨"""

        logger.info(f'New feedback received from user {message.from_user.id}: "{message.text}"')

        # Create inline keyboard for recipient
        markup = types.InlineKeyboardMarkup(row_width=3)
        
        # Create callback data with minimal necessary information
        answer_group_data = json.dumps({
            'action': 'answer_group'
        })
        
        answer_bot_data = json.dumps({
            'action': 'answer_bot',
            'user_id': message.from_user.id
        })
        
        # Create direct chat URL - this will open chat directly when button is clicked
        direct_chat_url = f"tg://user?id={message.from_user.id}"
        
        # Create buttons
        btn_answer_group = types.InlineKeyboardButton('Answer for Group', callback_data=answer_group_data)
        btn_answer_bot = types.InlineKeyboardButton('Answer in Bot', callback_data=answer_bot_data)
        
        # For direct chat, use URL button instead of callback button
        btn_direct_msg = types.InlineKeyboardButton('Direct Message', url=direct_chat_url)
        
        # Add buttons to markup
        markup.add(btn_answer_group, btn_answer_bot, btn_direct_msg)

        # Forward message to recipient with buttons
        bot.send_message(
            chat_id=recipient_id, 
            text=f'❗New feedback: "{message.text}"',
            reply_markup=markup
        )

        try:
            message.text.encode(encoding='utf-8')
        except UnicodeEncodeError:
            logger.error(f'Message from user {message.from_user.id} not saved due to encoding issues')
            bot.reply_to(message, 'An error occurred. Please try removing special characters and emojis.')
            return

        # Add message to storage
        date_str = str(dt.datetime.now().date())
        time_str = str(dt.datetime.now().time())[:-10]
        
        nonlocal file_data
        file_data = storage.add_message(file_data, message.text, date_str, time_str)
        logger.debug(f'Message from user {message.from_user.id} added to storage')
        
        # Reply to user
        bot.reply_to(message, answer)