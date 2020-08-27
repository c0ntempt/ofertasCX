import logging
from enum import Enum, auto

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler

from ofertascx.bot import Bot
from ofertascx import get_ventas, get_compras

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class States(Enum):
    START = auto()
    HELP = auto()
    VENTAS = auto()
    COMPRAS = auto()


keyboard_start = [[
    InlineKeyboardButton('Ventas', callback_data=str(States.VENTAS)),
    InlineKeyboardButton('Compras', callback_data=str(States.COMPRAS)),
    InlineKeyboardButton('Ayuda', callback_data=str(States.HELP)),
]]


class Messages:
    WELCOME = (
        '<b>Bienvenido a OfertasCX bot.</b>\n'
        'Este bot no esta relacionado de forma alguno con el proyecto o desarrolladores '
        'de la plataforma <a href="https://bit.ly/2ZtAyrq">CubaXchange</a>. '
        'Aqui podras encontrar de manera facil y actualizada las distintas ofertas que son publicadas'
        'en la plataforma, actualizada cada 10 minutos. Espero que les sirva de ayuda.'
    )

    VENTAS = (
        ''
    )

    COMPRAS = (
        ''
    )

    AYUDA = (
        ''
    )


def gen_oferta_msg(tipo='venta'):
    get_ofertas = get_ventas if tipo == 'venta' else get_compras

    msg = ''
    for oferta in get_ofertas():
        msg = msg + '{cripto} {valor}% - {usuario}\n'.format(
            cripto=oferta.get('cripto'),
            valor=oferta.get('valor'),
            usuario=oferta.get('usuario'),
            link=oferta.get('link')
        )
    return msg


class OfertasBot(Bot):
    def __init__(self, token, developer_id):
        super(OfertasBot, self).__init__(token, developer_id)

        dispatcher = self.updater.dispatcher
        dispatcher.add_error_handler(self.error_handler)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.command_start)],
            states={
                str(States.START): [
                    CallbackQueryHandler(self.command_ventas, pattern='^' + str(States.VENTAS) + '$'),
                    CallbackQueryHandler(self.command_compras, pattern='^' + str(States.COMPRAS) + '$'),
                    CallbackQueryHandler(self.command_help, pattern='^' + str(States.HELP) + '$'),
                ]
            },
            fallbacks=[CommandHandler('start', self.command_start)]
        )
        dispatcher.add_handler(conv_handler)

    def command_start(self, update: Update, context: CallbackContext):
        """Send message on `/start`."""
        # Get user that sent /start and log his name
        user = update.message.from_user
        logger.info("User %s started the conversation.", user.first_name)

        # Send message with text and appended InlineKeyboard
        update.message.reply_html(
            Messages.WELCOME,
            reply_markup=InlineKeyboardMarkup(keyboard_start)
        )
        return str(States.START)

    def command_help(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text='Help Text',
            reply_markup=InlineKeyboardMarkup(keyboard_start)
        )
        return str(States.START)

    # TODO Check msg length
    def command_ventas(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=gen_oferta_msg(),
            reply_markup=InlineKeyboardMarkup(keyboard_start),
            parse_mode=ParseMode.HTML
        )
        return str(States.START)

    # TODO Check msg length
    def command_compras(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=gen_oferta_msg('compra'),
            reply_markup=InlineKeyboardMarkup(keyboard_start),
            parse_mode=ParseMode.HTML
        )

        return str(States.START)
