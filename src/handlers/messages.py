import datetime as dt
import json
from telebot import TeleBot, types
from loguru import logger
from src.services.redis_service import RedisService
from src.services.storage_service import StorageService

def register_message_handlers(bot: TeleBot, storage: StorageService, recipient_id: int, redis_service: RedisService = None, block_service=None):
    """
    Registers message handlers for processing incoming feedback messages.

    Args:
        bot (TeleBot): The Telegram bot instance.
        storage (StorageService): Service for storing feedback messages.
        recipient_id (int): The recipient (admin) ID for forwarded messages.
        redis_service (RedisService, optional): Service for rate limiting. Defaults to None.
        block_service (BlockService, optional): Service for checking blocked users. Defaults to None.
    """
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        """
        Processes an incoming message by checking if the user is blocked,
        applying rate limits, validating content, and then forwarding the message
        to the admin with inline buttons (including a Block/Unblock button).

        Args:
            message: The incoming message from the user.
        """
        user_id = message.from_user.id

        # Check if user is blocked
        if block_service and block_service.is_blocked(user_id):
            logger.info(f"Blocked user {user_id} attempted to send a message.")
            return  # Ignore messages from blocked users
        
        # Rate limiting checks via Redis (if available)
        if redis_service:
            if is_limited_fast := redis_service.check_rate_limit(user_id, 'fast')[0]:
                logger.warning(f'User {user_id} exceeded fast rate limit')
                bot.reply_to(message, 'Please slow down. Try sending messages less frequently.')
                return
                
            if (is_limited_slow := redis_service.check_rate_limit(user_id, 'slow'))[0]:
                wait_time = redis_service.check_rate_limit(user_id, 'slow')[1]
                logger.warning(f'User {user_id} exceeded slow rate limit (3 messages/minute)')
                bot.reply_to(message, f'You have sent too many messages. Please wait {wait_time} seconds before trying again.')
                return

        # Basic validation of message content
        if not any(c.isalnum() for c in message.text):
            logger.warning(f'User {user_id} tried to send emoji-only message')
            bot.reply_to(message, 'Please include some text in your message, not just emojis.')
            return

        if len(message.text) > 500:
            logger.warning(f'User {user_id} tried to send message exceeding 500 chars')
            bot.reply_to(message, 'Sorry, your message is too long. Please divide it into several parts and try again.')
            return

        # Build the inline keyboard for the admin message
        markup = types.InlineKeyboardMarkup(row_width=4)
        btn_answer_group = types.InlineKeyboardButton(
            'Answer for Group', 
            callback_data=json.dumps({'action': 'answer_group'})
        )
        btn_answer_bot = types.InlineKeyboardButton(
            'Answer in Bot', 
            callback_data=json.dumps({'action': 'answer_bot', 'user_id': user_id})
        )
        btn_direct_msg = types.InlineKeyboardButton(
            'Direct Message', 
            url=f"tg://user?id={user_id}"
        )

        # Add block/unblock button based on current status
        if block_service:
            if block_service.is_blocked(user_id):
                btn_block = types.InlineKeyboardButton(
                    "Unblock User", 
                    callback_data=json.dumps({'action': 'unblock_user', 'user_id': user_id})
                )
            else:
                btn_block = types.InlineKeyboardButton(
                    "Block User", 
                    callback_data=json.dumps({'action': 'block_user', 'user_id': user_id})
                )
            markup.add(btn_answer_group, btn_answer_bot, btn_direct_msg, btn_block)
        else:
            markup.add(btn_answer_group, btn_answer_bot, btn_direct_msg)

        bot.send_message(
            chat_id=recipient_id, 
            text=f'❗New feedback: "{message.text}"',
            reply_markup=markup
        )

        try:
            message.text.encode(encoding='utf-8')
        except UnicodeEncodeError:
            logger.error(f'Message from user {user_id} not saved due to encoding issues')
            bot.reply_to(message, 'An error occurred. Please try removing special characters and emojis.')
            return

        date_str = str(dt.datetime.now().date())
        time_str = str(dt.datetime.now().time())[:-10]
        storage.add_message(message.text, date_str, time_str)
        logger.debug(f'Message from user {user_id} added to storage')
        
        bot.reply_to(message, f'Thank you! Your message: "{message.text}"\nHas been successfully recorded. You\'ll receive a response soon.✨')
        logger.info(f'New feedback received from user {user_id}: "{message.text}"')
