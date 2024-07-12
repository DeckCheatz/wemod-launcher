from strictyaml import load
from pathlib import Path
from xdg.BaseDirectory import save_config_path
from .logger import LoggingHandler


class Configuration(object):
    def __init__(self, cfg_path: str = save_config_path("wemod_launcher")):
        # Initialize logger for Config.
        self.__log = LoggingHandler(module_name=__name__).get_logger()
        self.__log.debug("Initializing configuration.")

        # TODO: Add try/except block for handling errors.
        path = Path(cfg_path)
        if not path.exists():
            path.mkdir()

        cfg_file = path / "config.yml"
        cfg_file.write_text("")
        self.__config = load(str(path)).data
        self.__log.debug("Configuration initialized.")

    def get(self, section, key):
        return self.__config[section][key]
