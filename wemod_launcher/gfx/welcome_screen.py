from xdg.BaseDirectory import save_cache_path
import FreeSimpleGUI as sg
import requests
from pathlib import Path
from ..utils.logger import LoggingHandler

class WelcomeScreenGfx(object):
    WEMOD_LOGO_URL: str = (
        "https://www.wemod.com/static/images/device-icons/favicon-192-ce0bc030f3.png"
    )

    def __init__(self):
        ## TODO: Cache this image.

        self.__logger = LoggingHandler(__name__).get_logger()

        cache_path = Path(save_cache_path("wemod_launcher")) / "assets/wemod_logo.png"
        if cache_path.exists():
            self.WEMOD_LOGO_RAW = open(str(cache_path), "rb").read()
        else:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.__logger.debug("Downloading logo to cache, and memory.")
            logo_raw = requests.get(self.WEMOD_LOGO_URL, stream=False).content
            open(str(cache_path), "wb").write(logo_raw)
            self.WEMOD_LOGO_RAW = open(str(cache_path), "rb").read()

        self.__logger.debug("WelcomeScreenGfx initialized")

    def run(self):
        sg.theme("systemdefault")

        return (
            sg.popup_ok_cancel(
                "Welcome to the WeMod Installer!\nPress ok to start the setup.",
                title="WeMod Launcher Setup",
                image=self.WEMOD_LOGO_RAW,
                icon=self.WEMOD_LOGO_RAW,
            )
            == "OK"
        )
