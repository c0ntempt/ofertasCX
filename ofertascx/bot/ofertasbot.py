import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, \
    Filters

from ofertascx import get_ventas, get_compras, Offers, filter_ventas, filter_compras, get_payment_types
from ofertascx.bot import Bot
from ofertascx.settings import MY_REFERRAL, URL_PUBLIC, PagoIntervals

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# States
START, VENTAS, COMPRAS, FILTER = map(chr, range(4))


# Callback data
VENTAS_CB, COMPRAS_CB, FILTER_CB, BACK, \
FILTER_MONEDA, FILTER_VALOR, FILTER_PAGO, \
FILTER_MONEDA_BTC, FILTER_MONEDA_LTC, FILTER_MONEDA_ETH, FILTER_MONEDA_USD, \
FILTER_VALOR_UP_TO_5, \
FILTER_VALOR_BETWEEN_5_AND_15, \
FILTER_VALOR_BEYOND_15 = map(chr, range(14))


keyboard_start = [[
    InlineKeyboardButton('Ventas', callback_data=VENTAS_CB),
    InlineKeyboardButton('Compras', callback_data=COMPRAS_CB),
]]

keyboard_oferta = [[
    InlineKeyboardButton('Filtrar', callback_data=FILTER_CB),
    InlineKeyboardButton('Volver', callback_data=BACK),
]]

keyboard_filtros = [
    [
        InlineKeyboardButton('Moneda', callback_data=FILTER_MONEDA),
        InlineKeyboardButton('Valor', callback_data=FILTER_VALOR),
        InlineKeyboardButton('Pago', callback_data=FILTER_PAGO),
    ], [
        InlineKeyboardButton('Volver', callback_data=BACK),
    ]
]


class Messages:
    WELCOME = (
        '<b>Bienvenido a OfertasCX bot.</b>\n'
        'Aqui podras encontrar de manera facil y actualizada las distintas ofertas que son publicadas '
        'en la plataforma.\nDatos actualizados cada 10 minutos. Espero que les sirva de ayuda.'
        '\nEste bot no esta relacionado de forma alguna con el proyecto o desarrolladores '
        'de <a href="' + MY_REFERRAL + '">CubaXchange</a>. '
    )

    OFFER = '<b>Ofertas de {0}</b>\n<a href="{1}">CubaXchange</a>\n\n'

    SELECT_COIN = ''

    WRONG_METHOD = 'Metodo de pago incorrecto, seleccione uno de la lista.'

    WRONG_OFFER = 'Tipo de oferta no encontrado'

    NO_OFFERS = 'No existe una oferta con esas caracteristicas'

    SELECT_PAYMENT = 'Seleccione el tipo de pago deseado:'


def construct_oferta_msg(ofertas, type_=Offers.VENTA):
    # TODO  Check for messages' length
    # TODO  Implement pagination

    if type_ not in Offers:
        raise Exception('Invalid offer type')

    msg = Messages.OFFER.format(type_, MY_REFERRAL)

    for oferta in ofertas:
        msg = msg + '{cripto} ({valor}%) - <code>{usuario}</code>\n'.format(
            cripto=oferta.get('cripto'),
            valor=oferta.get('valor'),
            usuario=oferta.get('usuario'),
        )
    return msg


def get_current_offer(prev_state) -> tuple:
    """Returns filter_offer callback and offer's type"""
    if not prev_state:
        raise Exception('Invalid prev state. Imposible to be here')

    if prev_state == VENTAS:
        filter_offer = filter_ventas
        type_ = Offers.VENTA
    elif prev_state == COMPRAS:
        filter_offer = filter_compras
        type_ = Offers.COMPRA
    else:
        raise Exception('Invalid state. That\'s imposible')

    return filter_offer, type_


# def clear_filters(filters):
#     for f in list(filters.keys()):
#         if f != 'offer':
#             filters.pop(f)
#     return filters


class OfertasBot(Bot):
    def __init__(self, token, developer_id):
        super(OfertasBot, self).__init__(token, developer_id)

        dispatcher = self.updater.dispatcher
        dispatcher.add_error_handler(self.error_handler)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.command_start)],
            states={
                START: [
                    CallbackQueryHandler(self.command_ventas, pattern='^' + VENTAS_CB + '$'),
                    CallbackQueryHandler(self.command_compras, pattern='^' + COMPRAS_CB + '$'),
                ],
                VENTAS: [
                    CallbackQueryHandler(self.command_filter, pattern='^' + FILTER_CB + '$'),
                    CallbackQueryHandler(self.command_start_inline, pattern='^' + BACK + '$'),
                ],
                COMPRAS: [
                    CallbackQueryHandler(self.command_filter, pattern='^' + FILTER_CB + '$'),
                    CallbackQueryHandler(self.command_start_inline, pattern='^' + BACK + '$'),
                ],
                FILTER: [
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + FILTER_MONEDA + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + FILTER_VALOR + '$'),

                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + FILTER_MONEDA_BTC + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + FILTER_MONEDA_LTC + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + FILTER_MONEDA_ETH + '$'),
                    CallbackQueryHandler(self.command_filter_moneda, pattern='^' + FILTER_MONEDA_USD + '$'),

                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + FILTER_VALOR_UP_TO_5 + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + FILTER_VALOR_BETWEEN_5_AND_15 + '$'),
                    CallbackQueryHandler(self.command_filter_valor, pattern='^' + FILTER_VALOR_BEYOND_15 + '$'),

                    CallbackQueryHandler(self.command_filter_pago, pattern='^' + FILTER_PAGO + '$'),
                    MessageHandler(Filters.text & ~Filters.command, self.command_filter_pago),

                    CallbackQueryHandler(self.command_back, pattern='^' + BACK + '$'),
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
        context.user_data['user_id'] = user.id

        return START

    def command_start_inline(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        query.edit_message_text(
            text=Messages.WELCOME,
            reply_markup=InlineKeyboardMarkup(keyboard_start),
            parse_mode=ParseMode.HTML
        )

        if context.user_data.get('filter'):
            context.user_data.pop('filter')

        context.user_data['prev_state'] = START

        return START

    def command_ventas(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        # context.user_data['filter'] = dict(offer=Offers.VENTA)

        query.edit_message_text(
            text=construct_oferta_msg(get_ventas(), Offers.VENTA),
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = VENTAS

        return VENTAS

    def command_compras(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        # context.user_data['filter'] = dict(offer=Offers.COMPRA)

        query.edit_message_text(
            text=construct_oferta_msg(get_compras(), Offers.COMPRA),
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        context.user_data['prev_state'] = COMPRAS

        return COMPRAS

    def command_filter(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        if context.user_data.get('prev_state') == VENTAS:
            msg = construct_oferta_msg(get_ventas(), Offers.VENTA)
        elif context.user_data.get('prev_state') == COMPRAS:
            msg = construct_oferta_msg(get_compras(), Offers.COMPRA)
        else:
            raise Exception('Tipo de oferta invalido')

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_filtros),
            parse_mode=ParseMode.HTML
        )

        return FILTER

    def command_filter_moneda(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        filter_offer, type_ = get_current_offer(context.user_data.get('prev_state', None))

        keyboard_filtro_moneda = [
            [
                InlineKeyboardButton('BTC', callback_data=FILTER_MONEDA_BTC),
                InlineKeyboardButton('LTC', callback_data=FILTER_MONEDA_LTC),
                InlineKeyboardButton('ETH', callback_data=FILTER_MONEDA_ETH),
                InlineKeyboardButton('USD', callback_data=FILTER_MONEDA_USD),
            ], [
                # InlineKeyboardButton('Pago', callback_data=FILTER_PAGO),
                InlineKeyboardButton('Volver', callback_data=BACK),
            ]
        ]

        if query.data == FILTER_MONEDA_BTC:
            offers = filter_offer(cripto='BTC')
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)
                # context.user_data['filter'].update(dict(cripto='BTC'))

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == FILTER_MONEDA_LTC:
            offers = filter_offer(cripto='LTC')
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)
                # context.user_data['filter'].update(dict(cripto='LTC'))

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == FILTER_MONEDA_ETH:
            offers = filter_offer(cripto='ETH')
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)
                # context.user_data['filter'].update(dict(cripto='ETH'))

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        elif query.data == FILTER_MONEDA_USD:
            offers = filter_offer(cripto='USD')
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)
                # context.user_data['filter'].update(dict(cripto='USD'))

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )
        else:
            if context.user_data.get('prev_state') == VENTAS:
                msg = construct_oferta_msg(get_ventas(), Offers.VENTA)
            elif context.user_data.get('prev_state') == COMPRAS:
                msg = construct_oferta_msg(get_compras(), Offers.COMPRA)
            else:
                raise Exception(Messages.WRONG_OFFER)

            query.edit_message_text(
                text=msg + '\n' + Messages.SELECT_COIN,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_moneda),
                parse_mode=ParseMode.HTML
            )

        return FILTER

    def command_filter_valor(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        filter_offer, type_ = get_current_offer(context.user_data.get('prev_state', None))

        keyboard_filtro_valor = [
            [
                InlineKeyboardButton('< 5', callback_data=FILTER_VALOR_UP_TO_5),
                InlineKeyboardButton('Entre 5 y 15', callback_data=FILTER_VALOR_BETWEEN_5_AND_15),
                InlineKeyboardButton('> 15', callback_data=FILTER_VALOR_BEYOND_15),
            ], [
                InlineKeyboardButton('Volver', callback_data=BACK),
            ]
        ]
        # msg = Messages.OFFER.format(type_, MY_REFERRAL)

        if query.data == FILTER_VALOR_UP_TO_5:
            offers = filter_offer(valor=PagoIntervals.MIN)
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )
        elif query.data == FILTER_VALOR_BETWEEN_5_AND_15:
            offers = filter_offer(valor=PagoIntervals.MID)
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)

            query.edit_message_text(
                text=msg,
                reply_markup=InlineKeyboardMarkup(keyboard_filtro_valor),
                parse_mode=ParseMode.HTML
            )
        elif query.data == FILTER_VALOR_BEYOND_15:
            offers = filter_offer(valor=PagoIntervals.MAX)
            if len(offers) == 0:
                msg = Messages.NO_OFFERS
            else:
                msg = construct_oferta_msg(offers, type_)

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

        return FILTER

    def command_filter_pago(self, update: Update, context: CallbackContext):

        if context.user_data.get('prev_state') == VENTAS:
            filters = dict(offer=Offers.VENTA)
        elif context.user_data.get('prev_state') == COMPRAS:
            filters = dict(offer=Offers.COMPRA)
        else:
            raise Exception('Tipo de oferta invalido')

        payment_types = get_payment_types(filters)

        # When used as callback: Show keyboard
        if update.callback_query:
            query = update.callback_query
            query.answer()

            keyboard = []
            for j in range(0, len(payment_types), 3):
                temp = []
                for i in range(3):
                    if j + i < len(payment_types):
                        temp.append(payment_types[j + i])
                keyboard.append(temp)

            context.bot.send_message(
                context.user_data.get('user_id'),
                Messages.SELECT_PAYMENT,
                reply_markup=ReplyKeyboardMarkup(keyboard)#, one_time_keyboard=True)
            )

            return FILTER

        else:   # Method as a MessageHandler
            payment = update.message.text

            if payment not in payment_types:
                msg = Messages.WRONG_METHOD
            else:
                filter_offer, type_ = get_current_offer(context.user_data.get('prev_state', None))
                filters.update(dict(pago=payment))

                offers = filter_offer(**filters)
                msg = construct_oferta_msg(offers, type_)

            context.bot.send_message(
                context.user_data.get('user_id'),
                msg,
                parse_mode=ParseMode.HTML
            )

    def command_back(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        msg = ''
        if context.user_data.get('prev_state') == VENTAS:
            msg = construct_oferta_msg(get_ventas(), Offers.VENTA)
        elif context.user_data.get('prev_state') == COMPRAS:
            msg = construct_oferta_msg(get_compras(), Offers.COMPRA)

        query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard_oferta),
            parse_mode=ParseMode.HTML
        )

        return str(context.user_data.get('prev_state'))

    def command_user_link(self, update: Update, context: CallbackContext):
        users = update.message.text.split(' ')
        if len(users) <= 1:
            update.message.reply_text('Introduzca al menos un usuario')
        else:
            msg = ''
            for i in range(1, len(users)):
                msg = msg + '{0}/{1}\n'.format(URL_PUBLIC, users[i])

            update.message.reply_text(msg)
