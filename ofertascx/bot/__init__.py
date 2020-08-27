import html
import json
import logging
import traceback

from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ParseMode, Update

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, token, developer_id):
        self.developer_id = developer_id

        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(token, use_context=True)

    def bind_commands(self):
        raise Exception('Not Implemented')

    def command_start(self, update: Update, context: CallbackContext):
        raise Exception('Not Implemented')

    def command_help(self, update: Update, context: CallbackContext):
        raise Exception('Not Implemented')

    def run(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        self.updater.idle()

    def error_handler(self, update: Update, context: CallbackContext):
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb = ''.join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        message = (
            'An exception was raised while handling an update\n'
            '<pre>update = {}</pre>\n\n'
            '<pre>context.chat_data = {}</pre>\n\n'
            '<pre>context.user_data = {}</pre>\n\n'
            '<pre>{}</pre>'
        ).format(
            html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
            html.escape(str(context.chat_data)),
            html.escape(str(context.user_data)),
            html.escape(tb)
        )

        # Finally, send the message
        context.bot.send_message(chat_id=self.developer_id, text=message, parse_mode=ParseMode.HTML)
