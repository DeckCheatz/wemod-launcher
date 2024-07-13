import FreeSimpleGUI as sg
import requests


class WelcomeScreenGfx(object):
    WEMOD_LOGO_URL: str = (
        "https://www.wemod.com/static/images/device-icons/favicon-192-ce0bc030f3.png"
    )

    def __init__(self):
        ## TODO: Cache this image.
        self.WEMOD_LOGO_RAW = requests.get(self.WEMOD_LOGO_URL, stream=False)

    def run(self):
        sg.theme("systemdefault")

        return (
            sg.popup_ok_cancel(
                "Welcome to the WeMod Installer!\nPress ok to start the setup.",
                title="WeMod Launcher Setup",
                image=self.WEMOD_LOGO_RAW.content,
                icon=self.WEMOD_LOGO_RAW.content,
            )
            == "OK"
        )
