from typing import Optional
from xdg.BaseDirectory import save_data_path
from path import Path
import logging
from os import environ


class LoggingHandler(object):
    def __init__(
        self,
        module_name: str = __name__,
        level: Optional[int] = None,
        log_file: str = save_data_path("wemod_launcher"),
    ):
        try:
            if environ["WEMOD_LAUNCHER_DEV_MODE"] is True:
                level = logging.DEBUG
            elif "WEMOD_LAUNCHER_LOG_LEVEL" in environ and level is None:
                env_log_level = environ["WEMOD_LAUNCHER_LOG_LEVEL"]
                match env_log_level:
                    case "DEBUG":
                        level = logging.DEBUG
                    case "INFO":
                        level = logging.INFO
                    case "WARNING":
                        level = logging.WARNING
                    case "ERROR":
                        level = logging.ERROR
                    case "CRITICAL":
                        level = logging.CRITICAL
                    case _:
                        level = logging.INFO
        except KeyError:
            pass 

        self.logger = logging.getLogger(f"wemod_launcher: {module_name}")
        self.logger.setLevel(level or logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(
            logging.FileHandler(
                Path(log_file).joinpath(f"wemod_launcher.log")
            )
        )

    def get_logger(self) -> logging.Logger:
        return self.logger
