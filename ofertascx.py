from ofertascx.bot.ofertasbot import OfertasBot
from ofertascx.settings import BOT_TOKEN, DEVELOPER_CHAT_ID


def main():
    bot = OfertasBot(BOT_TOKEN, DEVELOPER_CHAT_ID)
    bot.run()


if __name__ == '__main__':
    main()
