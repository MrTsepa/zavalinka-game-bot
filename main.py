import configparser
import logging
import pathlib

from bot.bot import Bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    debug = False
    if config['DEFAULT']['Debug'] == 'yes':
        config = config['DEBUG']
        debug = True
        logger.info('Using debug mode')
    else:
        config = config['PROD']
        logger.info('Using prod mode')

    with open(config.get('Token'), 'r') as f:
        TOKEN = f.readline()

    bot = Bot(TOKEN, pathlib.Path('assets'), debug=debug)
    bot.start()


if __name__ == '__main__':
    main()
