from wemod_launcher.utils.logger import LoggingHandler
from wemod_launcher.utils.configuration import Configuration
from wemod_launcher.utils.consts import Consts
from wemod_launcher.gfx.welcome_screen import WelcomeScreenGfx

log = LoggingHandler(__name__).get_logger()
cfg = Configuration()
consts = Consts()


def main():
    log.info("Welcome to WeMod Launcher!")

    WelcomeScreenGfx().run()
