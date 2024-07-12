from strictyaml import load
from path import Path
from xdg.BaseDirectory import save_config_path
from .logger import LoggingHandler


class Configuration(object):
    def __init__(self, path: str = save_config_path("wemod_launcher")):
        # Initialize logger for Config.
        self.__log = LoggingHandler("Configuration").get_logger()
        self.__log.debug("Initializing configuration.")
        # TODO: Add try/except block for handling errors.
        path = Path(path)
        try:
            path.mkdir()
        except FileExistsError:
            self.__log.debug("Configuration directory already exists - ignoring!")
            pass
        cfg_file = path / "config.yml"
        cfg_file.write_lines([""])
        self.__config = load(Path(cfg_file).text()).data
        self.__log.debug("Configuration initialized.")

    def get(self, section, key):
        return self.__config[section][key]
