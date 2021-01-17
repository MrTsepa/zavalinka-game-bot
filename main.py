from private_messages_bot.private_messages_bot import PrivateMessagesBot

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    with open('.token', 'r') as f:
        TOKEN = f.readline()

    bot = PrivateMessagesBot(TOKEN)
    bot.start()


if __name__ == '__main__':
    main()
