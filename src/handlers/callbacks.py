import json
from telebot import TeleBot, types
from loguru import logger

def register_callback_handlers(bot: TeleBot, block_service):
    """
    Registers callback query handlers for the bot.
    
    Args:
        bot (TeleBot): The Telegram bot instance.
        block_service (BlockService): Service for managing blocked users.
    """
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        """
        Processes incoming callback queries and routes them to the appropriate handler.
        
        Args:
            call: The callback query received from Telegram.
        """
        try:
            data = json.loads(call.data)
            # Check if using the compact callback payload
            if 'a' in data:
                action = data.get('a')
                identifier = data.get('i')
                user_id = data.get('u')
                if action == 'b':
                    if block_service.block_user(identifier):
                        bot.answer_callback_query(call.id, "User has been blocked.")
                    else:
                        bot.answer_callback_query(call.id, "User is already blocked.")
                elif action == 'u':
                    if block_service.unblock_user(identifier):
                        bot.answer_callback_query(call.id, "User has been unblocked.")
                    else:
                        bot.answer_callback_query(call.id, "User is not blocked.")
                
                # Rebuild the inline keyboard with updated block/unblock button
                btn_answer_group = types.InlineKeyboardButton(
                    "Group",
                    callback_data=json.dumps({'action': 'answer_group'})
                )
                btn_answer_bot = types.InlineKeyboardButton(
                    "In Bot",
                    callback_data=json.dumps({'action': 'answer_bot', 'user_id': user_id})
                )
                btn_direct_msg = types.InlineKeyboardButton(
                    "DM",
                    url=f"tg://user?id={user_id}"
                )
                if block_service.is_blocked(identifier):
                    btn_block = types.InlineKeyboardButton(
                        "Unblock",
                        callback_data=json.dumps({'a': 'u', 'i': identifier, 'u': user_id})
                    )
                else:
                    btn_block = types.InlineKeyboardButton(
                        "Block",
                        callback_data=json.dumps({'a': 'b', 'i': identifier, 'u': user_id})
                    )
                new_markup = types.InlineKeyboardMarkup(row_width=4)
                new_markup.add(btn_answer_group, btn_answer_bot, btn_direct_msg, btn_block)
                
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=new_markup
                )
            else:
                # Fallback to previous actions for answering messages
                action = data.get('action')
                if action == 'answer_group':
                    original_message = call.message.text
                    question = original_message.split('"')[1]
                    bot.answer_callback_query(call.id)
                    msg = bot.send_message(
                        call.from_user.id,
                        f"Please reply with your answer to:\n\n<i>{question}</i>",
                        parse_mode='HTML'
                    )
                    bot.register_next_step_handler(
                        msg,
                        process_group_answer,
                        bot=bot,
                        question=question
                    )
                elif action == 'answer_bot':
                    question = call.message.text.split('"')[1]
                    user_id = data.get('user_id')
                    bot.answer_callback_query(call.id)
                    msg = bot.send_message(
                        call.from_user.id,
                        f"Please reply with your answer to send to the user:\n\n<i>{question}</i>",
                        parse_mode='HTML'
                    )
                    bot.register_next_step_handler(
                        msg,
                        process_bot_answer,
                        user_id=user_id,
                        question=question,
                        bot=bot
                    )
        except Exception as e:
            logger.error(f"Error processing callback: {e}")
            bot.answer_callback_query(call.id, "An error occurred while processing your request.")

def process_group_answer(message, bot, question):
    """
    Formats and sends a group answer based on the user's reply.
    
    Args:
        message: The message containing the user's reply.
        bot (TeleBot): The Telegram bot instance.
        question (str): The original question that was answered.
    """
    formatted_response = f"<i>Q: {question}</i>\n\n{message.text}"
    
    bot.send_message(
        message.chat.id,
        "Here's your formatted answer for the group. You can copy or forward it:",
        parse_mode='HTML'
    )
    bot.send_message(
        message.chat.id,
        formatted_response,
        parse_mode='HTML'
    )
    logger.info(f"Group answer formatted for question: {question[:30]}...")

def process_bot_answer(message, user_id, question, bot):
    """
    Sends the user's reply as an answer directly to the intended recipient.
    
    Args:
        message: The message containing the user's reply.
        user_id (int): The ID of the user to receive the answer.
        question (str): The original question.
        bot (TeleBot): The Telegram bot instance.
    """
    try:
        bot.send_message(
            user_id,
            f"Reply to your question:\n\n<i>{question}</i>\n\n{message.text}",
            parse_mode='HTML'
        )
        bot.send_message(
            message.chat.id,
            "Your answer has been sent to the user!",
            parse_mode='HTML'
        )
        logger.info(f"Answer sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send answer to user {user_id}: {e}")
        bot.send_message(
            message.chat.id,
            f"Failed to send your answer. Error: {str(e)}",
            parse_mode='HTML'
        )
