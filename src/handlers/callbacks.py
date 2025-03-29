import json
from telebot import TeleBot
from loguru import logger

def register_callback_handlers(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        try:
            data = json.loads(call.data)
            action = data.get('action')
            original_message = call.message.text
            question = original_message.split('"')[1]
            
            if action == 'answer_group':
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