import logging
from enum import Enum, auto

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler

from ofertascx.bot import Bot
from ofertascx import get_ventas, get_compras
from ofertascx.settings import MY_REFERRAL

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class States(Enum):
    START = auto()
    # HELP = auto()
    VENTAS = auto()
    COMPRAS = auto()
    FILTER = auto()


# Callback data
class Stage(Enum):
    VENTAS = auto()
    COMPRAS = auto()
    FILTER = auto()
    BACK = auto()
    FILTER_MONEDA = auto()
    FILTER_VALOR = auto()
    FILTER_PAGO = auto()


keyboard_start = [[
    InlineKeyboardButton('Ventas', callback_data=str(Stage.VENTAS)),
    InlineKeyboardButton('Compras', callback_data=str(Stage.COMPRAS)),
]]

keyboard_oferta = [[
    InlineKeyboardButton('Filtrar', callback_data=str(Stage.FILTER)),
    InlineKeyboardButton('Volver', callback_data=str(Stage.BACK)),
]]

keyboard_filtros = [
    [
        InlineKeyboardButton('Moneda', callback_data=str(Stage.FILTER_MONEDA)),
        InlineKeyboardButton('Valor', callback_data=str(Stage.FILTER_VALOR)),
        InlineKeyboardButton('Pago', callback_data=str(Stage.FILTER_PAGO)),
    ], [
        InlineKeyboardButton('Volver', callback_data=str(Stage.BACK)),
    ]

]


# TODO  Check for messages' length
# TODO  Implement pagination

class Messages:
    WELCOME = (
        '<b>Bienvenido a OfertasCX bot.</b>\n'
        'Este bot no esta relacionado de forma alguna con el proyecto o desarrolladores '
        'de <a href="' + MY_REFERRAL + '">CubaXchange</a>. '
        'Aqui podras encontrar de manera facil y actualizada las distintas ofertas que son publicadas '
        'en la plataforma.\nDatos actualizados cada 10 minutos. Espero que les sirva de ayuda.'
    )


def gen_oferta_msg(tipo='venta'):   # TODO Avoid hardcode this prone to error if tipo dont match 'compra'
    get_ofertas = get_ventas if tipo == 'venta' else get_compras

    msg = '<b>Ofertas de {0}</b>\n<a href="{1}">CubaXchange</a>\n\n'.format(tipo, MY_REFERRAL)
    for oferta in get_ofertas():
        msg = msg + '{cripto} ({valor}%) - <pre>{usuario}</pre>\n'.format(
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
                    CallbackQueryHandler(self.command_ventas, pattern='^' + str(Stage.VENTAS) + '$'),
                    CallbackQueryHandler(self.command_compras, pattern='^' + str(Stage.COMPRAS) + '$'),
                ],
                str(States.VENTAS): [
                    CallbackQueryHandler(self.command_filter, pattern='^' + str(Stage.FILTER) + '$'),
                    CallbackQueryHandler(self.command_start_inline, pattern='^' + str(Stage.BACK) + '$'),
                ],
                str(States.COMPRAS): [
                    CallbackQueryHandler(self.command_filter, pattern='^' + str(Stage.FILTER) + '$'),
                    CallbackQueryHandler(self.command_start_inline, pattern='^' + str(Stage.BACK) + '$'),
                ],
                str(States.FILTER): [
                    CallbackQueryHandler(self.command_filter, pattern='^' + str(Stage.FILTER_MONEDA) + '$'),
                    CallbackQueryHandler(self.command_filter, pattern='^' + str(Stage.FILTER_VALOR) + '$'),
                    CallbackQueryHandler(self.command_filter, pattern='^' + str(Stage.FILTER_PAGO) + '$'),
                    CallbackQueryHandler(self.command_back, pattern='^' + str(Stage.BACK) + '$'),
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

        context.user_data['prev_state'] = States.VENTAS

        return str(States.START)

    def command_start_inline(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=Messages.WELCOME,
            reply_markup=InlineKeyboardMarkup(keyboard_start),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.START

        return str(States.START)

    def command_ventas(self, update: Update, context: CallbackContext):
        logger.info('command_ventas')
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=gen_oferta_msg(),
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.VENTAS

        return str(States.VENTAS)

    def command_compras(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=gen_oferta_msg('compra'),
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.COMPRAS

        return str(States.COMPRAS)

    def command_filter(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        if context.user_data.get('prev_state') == States.VENTAS:
            msg = gen_oferta_msg()
        elif context.user_data.get('prev_state') == States.COMPRAS:
            msg = gen_oferta_msg('compra')

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_filtros),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.VENTAS

        return str(States.FILTER)

    def command_filter_moneda(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text='Seleccione',
            reply_markup=InlineKeyboardMarkup(keyboard_filtros),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.VENTAS

        return str(States.VENTAS)

    def command_back(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        if context.user_data.get('prev_state') == States.VENTAS:
            msg = gen_oferta_msg()
        elif context.user_data.get('prev_state') == States.COMPRAS:
            msg = gen_oferta_msg('compra')

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        return str(context.user_data.get('prev_state'))
