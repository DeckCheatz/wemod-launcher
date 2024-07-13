import os
from xdg.BaseDirectory import save_data_path
from pathlib import Path
import logging
from os import environ, getenv


class LoggingHandler(object):
    def __init__(
        self,
        module_name: str,
        level: int = 0,
        log_dir: str = save_data_path("wemod-launcher"),
    ):
        if not module_name or module_name.strip() == "":
            print("Module name is required!")
            print("This IS a bug, contact upstream devs.")
        try:
            if (
                getenv("WEMOD_LAUNCHER_DEV_MODE", "false").lower()
                in ("true", "1", "t")
                and level == 0
            ):
                level = logging.DEBUG
            elif "WEMOD_LAUNCHER_LOG_LEVEL" in environ and level == 0:
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
            level = logging.INFO
            pass

        log_base = Path(log_dir)
        if not log_base.exists():
            log_base.mkdir()

        logFormatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(name)s: %(message)s"
        )
        root_logger = logging.getLogger(module_name)

        file_handler = logging.FileHandler(
            os.getenv(
                "WEMOD_LAUNCHER_LOG_FILE",
                str(log_base / "wemod-launcher.log"),
            )
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logFormatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logFormatter)

        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.__logger = root_logger
        root_logger.debug(
            f"Logger for module ({module_name}) initialized with log level ({level})"
        )

    def get_logger(self) -> logging.Logger:
        return self.__logger
