import os
from .configuration import Configuration
from pathlib import Path


class Consts:
    CFG = Configuration()
    SCRIPT_RUNTIME_DIR: Path = Path(
        os.path.dirname(os.path.realpath(__file__))
    ).expanduser()
    STEAM_COMPAT_DATA_DIR: Path = Path(
        os.getenv(
            "STEAM_COMPAT_DATA_PATH",
            CFG.get_key(["steam", "compat_data_dir"]),
        )
    ).expanduser()
