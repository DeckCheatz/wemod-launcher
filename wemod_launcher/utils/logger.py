from typing import Optional
from xdg.BaseDirectory import save_data_path
from path import Path
import logging
from os import environ, getenv


class LoggingHandler(object):
    def __init__(
        self,
        module_name: str,
        level: int = 20,
        log_dir: Optional[str] = save_data_path("wemod_launcher"),
    ):
        if not module_name:
            print("Module name is required!")
            print("This IS a bug, contact upstream devs.")
        module_name = "wemod_launcher_{}".format(module_name.replace(".", "_"))
        try:
            if getenv("WEMOD_LAUNCHER_DEV_MODE", "False").lower() in ('true', '1', 't') == True and level is None:
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
            else:
                level = logging.INFO
        except KeyError:
            pass 

        log_dir = Path(log_dir)
        if not log_dir.exists():
            log_dir.mkdir()

        self.__logger = logging.getLogger(module_name)

        file_handler = logging.FileHandler(
                log_dir / "wemod_launcher.log")
        file_handler.setLevel(level if level else logging.INFO)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(level if level else logging.INFO)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(stdout_handler)

    def get_logger(self) -> logging.Logger:
        return self.__logger
