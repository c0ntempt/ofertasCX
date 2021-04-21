from ofertascx.settings import MY_REFERRAL, EMOJI_THUMBS_UP, EMOJI_THUMBS_DOWN


# TODO Look for better variable names 0_o
class Messages:
    WELCOME = (
        '<b>Bienvenido a OfertasHX bot.</b>\n'
        'Aqui podras encontrar de manera facil y actualizada las distintas ofertas que son publicadas '
        'en la plataforma.\nDatos actualizados cada 10 minutos. Espero que les sirva de ayuda.'
        '\nEste bot no esta asociado a los desarrolladores '
        'de <a href="' + MY_REFERRAL + '">HeavenEX</a>. '
    )

    HELP = """
<b>Comandos para interactuar con el bot</b>

/start - Inicia conversacion con el bot, muestra mensaje interactivo mediante botones.

/link user[ user2 ...] - Provee enlace del perfil publico del(de los) usuario(s) especificado(s) (note que no comprueba que el usuario existe realmente)
    
/user user - Devuelve informacion del perfil publico del usuario especificado."""

    OFFER = '<b>Ofertas de {0}</b>\n<a href="{1}">HeavenEX</a>\n\n'

    WRONG_METHOD = 'Metodo de pago incorrecto, seleccione uno de la lista.'

    WRONG_OFFER = 'Tipo de oferta no encontrado'

    NO_OFFERS = 'No existe una oferta con esas caracteristicas'

    SELECT_PAYMENT = 'Seleccione el tipo de pago deseado:'

    TYPE_USER = 'Introduzca al menos un usuario'

    USER_PROFILE = '{kyc}<b>{username}</b>\n'\
                   '%s {trust} %s {distrust}' % (EMOJI_THUMBS_UP, EMOJI_THUMBS_DOWN)