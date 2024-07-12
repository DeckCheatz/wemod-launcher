from typing import Optional
from xdg.BaseDirectory import save_data_path
from pathlib import Path
import logging
from os import environ, getenv


class LoggingHandler(object):
    def __init__(
        self,
        module_name: str,
        level: Optional[int] = None,
        log_dir: Optional[str] = save_data_path("wemod-launcher"),
    ):
        if not module_name:
            print("Module name is required!")
            print("This IS a bug, contact upstream devs.")
        module_name = "wemod_launcher_{}".format(module_name.replace(".", "_"))
        try:
            if environ["WEMOD_LAUNCHER_DEV_MODE"].lower() in ('true', '1', 't') and level is None:
                level = logging.DEBUG
                print(level)
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
            print("Log level: ", level)
        except KeyError:
            level = logging.INFO
            pass 

        log_dir = Path(log_dir)
        if not log_dir.exists():
            log_dir.mkdir()

        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(name)s: %(message)s")
        root_logger = logging.getLogger(module_name)

        file_handler = logging.FileHandler(
                str(log_dir / "wemod-launcher.log"))
        file_handler.setLevel(level)
        file_handler.setFormatter(logFormatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logFormatter)

        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.__logger = root_logger
        root_logger.debug(f"Logger for module ({module_name}) initialized with log level ({level})")
        

    def get_logger(self) -> logging.Logger:
        return self.__logger
