import logging
from enum import Enum, auto

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler

from ofertascx.bot import Bot
from ofertascx import get_ventas, get_compras, Offers, filter_ventas, filter_compras
from ofertascx.settings import MY_REFERRAL, URL_PUBLIC

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

    FILTER_MONEDA_BTC = auto()
    FILTER_MONEDA_LTC = auto()
    FILTER_MONEDA_ETH = auto()
    FILTER_MONEDA_USD = auto()

    FILTER_VALOR_UP_TO_5 = auto()           # VALOR <= 5
    FILTER_VALOR_BETWEEN_5_AND_15 = auto()  # 5 < VALOR <= 15
    FILTER_VALOR_BEYOND_15 = auto()         # VALOR > 15


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
        # InlineKeyboardButton('Pago', callback_data=str(Stage.FILTER_PAGO)),
    ], [
        InlineKeyboardButton('Volver', callback_data=str(Stage.BACK)),
    ]
]


class Messages:
    WELCOME = (
        '<b>Bienvenido a OfertasCX bot.</b>\n'
        'Este bot no esta relacionado de forma alguna con el proyecto o desarrolladores '
        'de <a href="' + MY_REFERRAL + '">CubaXchange</a>. '
        'Aqui podras encontrar de manera facil y actualizada las distintas ofertas que son publicadas '
        'en la plataforma.\nDatos actualizados cada 10 minutos. Espero que les sirva de ayuda.'
    )


def gen_oferta_msg(type_=Offers.VENTA):
    if type_ not in Offers:
        raise Exception('Invalid offer type')
    get_ofertas = get_ventas if type_ == Offers.VENTA else get_compras

    msg = '<b>Ofertas de {0}</b>\n<a href="{1}">CubaXchange</a>\n\n'.format(type_, MY_REFERRAL)
    msg = msg + construct_oferta_msg(get_ofertas())
    return msg


def construct_oferta_msg(ofertas):
    # TODO  Check for messages' length
    # TODO  Implement pagination

    msg = ''
    for oferta in ofertas:
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

        # TODO Improve all this
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
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + str(Stage.FILTER_MONEDA) + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + str(Stage.FILTER_VALOR) + '$'),
                    # CallbackQueryHandler(self.command_filter_pago, pattern='^' + str(Stage.FILTER_PAGO) + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + str(Stage.FILTER_MONEDA_BTC) + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + str(Stage.FILTER_MONEDA_LTC) + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + str(Stage.FILTER_MONEDA_ETH) + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + str(Stage.FILTER_MONEDA_USD) + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + str(Stage.FILTER_VALOR_UP_TO_5) + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + str(Stage.FILTER_VALOR_BETWEEN_5_AND_15) + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + str(Stage.FILTER_VALOR_BEYOND_15) + '$'),
                    CallbackQueryHandler(self.command_back, pattern='^' + str(Stage.BACK) + '$'),
                ]
            },
            fallbacks=[CommandHandler('start', self.command_start)]
        )
        dispatcher.add_handler(conv_handler)

        dispatcher.add_handler(CommandHandler('link', self.command_user_link))

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

        context.user_data['prev_state'] = None

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
            text=gen_oferta_msg(Offers.COMPRA),
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = States.COMPRAS

        return str(States.COMPRAS)

    def command_filter(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        msg = ''
        if context.user_data.get('prev_state') == States.VENTAS:
            msg = gen_oferta_msg(Offers.VENTA)
        elif context.user_data.get('prev_state') == States.COMPRAS:
            msg = gen_oferta_msg(Offers.COMPRA)

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_filtros),
            parse_mode=ParseMode.HTML
        )

        return str(States.FILTER)

    def command_filter_moneda(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        prev_state = context.user_data.get('prev_state')
        if not prev_state:
            raise Exception('Invalid prev state. Imposible to be here')

        filter_offer = None
        if prev_state == States.VENTAS:
            filter_offer = filter_ventas
        elif prev_state == States.COMPRAS:
            filter_offer = filter_compras
        else:
            raise Exception('Invalid state. That\'s imposible')

        # TODO Wired currencies
        keyboard_filtro_moneda = [
            [
                InlineKeyboardButton('BTC', callback_data=str(Stage.FILTER_MONEDA_BTC)),
                InlineKeyboardButton('LTC', callback_data=str(Stage.FILTER_MONEDA_LTC)),
                InlineKeyboardButton('ETH', callback_data=str(Stage.FILTER_MONEDA_ETH)),
                InlineKeyboardButton('USD', callback_data=str(Stage.FILTER_MONEDA_USD)),
            ], [
                InlineKeyboardButton('Volver', callback_data=str(Stage.BACK)),
            ]
        ]

        if query.data == str(Stage.FILTER_MONEDA_BTC):
            offers = filter_offer(cripto='BTC')
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == str(Stage.FILTER_MONEDA_LTC):
            offers = filter_offer(cripto='LTC')
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == str(Stage.FILTER_MONEDA_ETH):
            offers = filter_offer(cripto='ETH')
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == str(Stage.FILTER_MONEDA_USD):
            offers = filter_offer(cripto='USD')
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        else:
            query.edit_message_text(
                text='Seleccione moneda',
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )

        return str(States.FILTER)

    def command_filter_valor(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        prev_state = context.user_data.get('prev_state')
        if not prev_state:
            raise Exception('Invalid prev state. Imposible to be here')

        filter_offer = None
        if prev_state == States.VENTAS:
            filter_offer = filter_ventas
        elif prev_state == States.COMPRAS:
            filter_offer = filter_compras
        else:
            raise Exception('Invalid state. That\'s imposible')

        # TODO Wired currencies
        keyboard_filtro_valor = [
            [
                InlineKeyboardButton('< 5', callback_data=str(Stage.FILTER_VALOR_UP_TO_5)),
                InlineKeyboardButton('Entre 5 y 15', callback_data=str(Stage.FILTER_VALOR_BETWEEN_5_AND_15)),
                InlineKeyboardButton('> 15', callback_data=str(Stage.FILTER_VALOR_BEYOND_15)),
            ], [
                InlineKeyboardButton('Volver', callback_data=str(Stage.BACK)),
            ]
        ]

        if query.data == str(Stage.FILTER_VALOR_UP_TO_5):
            offers = filter_offer(valor=dict(max=5))
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )
        elif query.data == str(Stage.FILTER_VALOR_BETWEEN_5_AND_15):
            offers = filter_offer(valor=dict(min=5, max=15))
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )
        elif query.data == str(Stage.FILTER_VALOR_BEYOND_15):
            offers = filter_offer(valor=dict(min=15))
            if len(offers) == 0:
                msg = 'No existe una oferta con esas caracteristicas'
            else:
                msg = construct_oferta_msg(offers)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )
        else:
            query.edit_message_text(
                text='Seleccione intervalo',
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )

        return str(States.FILTER)

    def command_back(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        # TODO Avoid code duplication
        msg = ''
        if context.user_data.get('prev_state') == States.VENTAS:
            msg = gen_oferta_msg(Offers.VENTA)
        elif context.user_data.get('prev_state') == States.COMPRAS:
            msg = gen_oferta_msg(Offers.COMPRA)

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        return str(context.user_data.get('prev_state'))

    def command_user_link(self, update: Update, context: CallbackContext):
        print(update.message.text)
        users = update.message.text.split(' ')
        print(users)
        print(len(users))
        if len(users) <= 1:
            update.message.reply_text('Introduzca al menos un usuario')
        else:
            msg = ''
            for i in range(1, len(users)):
                msg = msg + '{0}/{1}\n'.format(URL_PUBLIC, users[i])

            update.message.reply_text(msg)
