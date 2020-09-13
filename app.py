import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.callbackquery import CallbackQuery
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackqueryhandler import CallbackQueryHandler

def cbStart(update, context):
    # creating list of input buttons
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.inlinekeyboardbutton.html
    keyboard = [[
        InlineKeyboardButton("Option 1", callback_data='1'),
        InlineKeyboardButton("Option 2", callback_data='2'),
        InlineKeyboardButton("Option 3", callback_data='3'),
        InlineKeyboardButton("Option 4", callback_data='4'),
    ]]

    # creating a reply markup of inline keyboard options
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.inlinekeyboardmarkup.html
    reply_markup = InlineKeyboardMarkup(keyboard)

    # sending the message to the current chat id
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.message.html#telegram.Message.reply_text
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    pass

def button(update, context):
    """
    callback method handling button press
    """
    # getting the callback query
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.callbackquery.html
    query: CallbackQuery = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.callbackquery.html#telegram.CallbackQuery.answer
    query.answer()

    # editing message sent by the bot
    # documentation: https://python-telegram-bot.readthedocs.io/en/stable/telegram.callbackquery.html#telegram.CallbackQuery.edit_message_text
    query.edit_message_text(text="Selected option: {}".format(query.data))

def cbCaps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def cbSetTimer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def cbUnsetTimer(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def main():
    
    #init logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    #init telegram bot creds
    updater = Updater(token='insert token here', use_context=True)
    dispatcher = updater.dispatcher

    #init and register handlers
    dispatcher.add_handler(CommandHandler('start', cbStart))
    dispatcher.add_handler(CommandHandler('caps', cbCaps))
    dispatcher.add_handler(CommandHandler("set", cbSetTimer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("unset", cbUnsetTimer, pass_chat_data=True))


    #start event loop
    updater.start_polling()

if __name__ == '__main__':
    main()