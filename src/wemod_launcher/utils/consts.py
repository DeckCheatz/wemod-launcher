import os
from wemod_launcher.utils.configuration import Configuration
from pathlib import Path


class Consts:
    CFG = Configuration()
    SCRIPT_RUNTIME_DIR: Path = Path(
        os.path.dirname(os.path.realpath(__file__))
    )
    SCRIPT_PATH: Path = Path(os.path.realpath(__file__))
    STEAM_COMPAT_DATA_DIR: Path = Path(
        os.getenv(
            "STEAM_COMPAT_DATA_PATH",
            CFG.get_key(["steam", "compat_data_dir"]),
        )
        or Path.home() / ".steam/steam/steamapps/compatdata"
    ).expanduser()
