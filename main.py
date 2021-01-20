import logging
import pathlib

from bot.bot import Bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    with open('.token', 'r') as f:
        TOKEN = f.readline()

    bot = Bot(TOKEN, pathlib.Path('assets'))
    bot.start()


if __name__ == '__main__':
    main()
