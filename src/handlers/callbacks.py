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
            action = data.get('action')
            
            # Actions for answering messages
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
            
            # Actions for blocking/unblocking users
            elif action in ['block_user', 'unblock_user']:
                user_id = int(data.get('user_id'))
                if action == 'block_user':
                    block_service.block_user(user_id)
                    bot.answer_callback_query(call.id, "User has been blocked.")
                else:
                    block_service.unblock_user(user_id)
                    bot.answer_callback_query(call.id, "User has been unblocked.")
                
                # Rebuild the inline keyboard based on the new block status
                btn_answer_group = types.InlineKeyboardButton(
                    "Answer for Group",
                    callback_data=json.dumps({'action': 'answer_group'})
                )
                btn_answer_bot = types.InlineKeyboardButton(
                    "Answer in Bot",
                    callback_data=json.dumps({'action': 'answer_bot', 'user_id': user_id})
                )
                btn_direct_msg = types.InlineKeyboardButton(
                    "Direct Message",
                    url=f"tg://user?id={user_id}"
                )
                # If the user is now blocked, show "Unblock User", otherwise show "Block User"
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
                new_markup = types.InlineKeyboardMarkup(row_width=4)
                new_markup.add(btn_answer_group, btn_answer_bot, btn_direct_msg, btn_block)
                
                # Update the message's reply markup with the new inline keyboard
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=new_markup
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
