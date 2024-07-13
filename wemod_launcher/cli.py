from .utils.logger import LoggingHandler
from .utils.configuration import Configuration
from .utils.consts import Consts
from .gfx.welcome_screen import WelcomeScreenGfx

log = LoggingHandler(__name__).get_logger()
cfg = Configuration()
consts = Consts()


def main():
    log.info("Welcome to WeMod Launcher!")

    print(consts.STEAM_COMPAT_DATA_DIR)

    WelcomeScreenGfx().run()
