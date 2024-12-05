#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-only

from configuration import ConfigManager
from consts import Constants
from pathlib import Path
import datetime
import logging
import sys
import os

CT, CM = None, None
CT = Constants()
CM = ConfigManager()

def Logger():
    # Define and register custom logging levels
    CustomLogger.register_custom_levels({
        'DOWNLOAD': logging.INFO - 3,
        'BUILDING': logging.INFO - 4,
        'GUI_CONSOLE': logging.INFO - 5,
        'STEAM': logging.INFO - 6
    })

    log_obj = CustomLogger()
    try:
        log_obj.info("The logger was instantiated", module="logger")
    except Exception as e:
        print(f"{CT.AppName}: Unrecoverable Error, Logger not working:\n{e}")
        exit(1)

    crit = False
    for msg in log_obj.futuremsg:
        log_obj.mlog(msg[0], "logger", msg[1])
        if msg[1] == "CRITICAL":
            crit = True
    if crit:
        exit(1)

    log_obj.futuremsg = []
    return log_obj


class CustomLogger(logging.Logger):
    def __init__(self):
        name = CT.app_name
        super().__init__(name)
        self.futuremsg = []

        level = CM.log_level
        self.list_levels()

        if level in self.levels.keys() or level in self.levels:
            self.setLevel(level)
        elif level == None:
            self.setLevel(logging.INFO)
        else:
            self.futuremsg.append([logging.WARN, f"The provided log level {level} was not found, using INFO level\nThe available levels are:\n{self.levels}"])
            self.setLevel(logging.INFO)

        log_dir = CM.log_dir
        if log_dir == None:
            log_dir = CT.log_dir
        else:
            log_dir = Path(log_dir)

        if not log_dir.is_absolute():
            rel = CM.log_rel
            if rel:
                log_dir = CT.git_base / log_dir
            else:
                log_dir = CT.global_conf_dir / log_dir

        log_dir.mkdir(mode=0o774, parents=True, exist_ok=True)
        os.chmod(log_dir, 0o774)

        log_name = CM.log_name
        if not log_name:
            # Create a file handler with a filename that includes the current time
            log_file_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            CM.log_name = log_file_time + ".log"

        log_file = log_dir / CM.log_name

        try:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(mmodule)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.addHandler(handler)
        except Exception as e:
            self.futuremsg.append([logging.CRITICAL,f"Error, can't create log file: {e}"])

        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s | %(mmodule)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        self.addHandler(console_handler)

    @staticmethod
    def register_custom_levels(levels):
        """Register custom logging levels dynamically."""
        for name, level in levels.items():
            logging.addLevelName(level, name)
            #CustomLogger.CUSTOM_LEVELS[name] = level

    def mlog(self, level, module = None, message=""):
        if not module:
            module = "main"
        strmodule = str(module).replace("\n"," ").upper()

        strmsg = str(message)
        splitmsg = strmsg.split("\n")
        filteredmsg = []
        for msg in splitmsg:
            if msg:
                filteredmsg.append(msg)

        if len(filteredmsg) < 1 or (len(filteredmsg) == 1 and not filteredmsg[0]):
            self.log(level, f"Empty message was logged for the module {strmodule}", extra={'mmodule': 'LOGGER'})
        elif len(filteredmsg) == 1:
            self.log(level, f"{filteredmsg[0]}", extra={'mmodule': strmodule})
        elif len(filteredmsg) > 1:
            self.log(level, f"Logging {len(filteredmsg)} Lines for the module {strmodule}", extra={'mmodule': 'LOGGER'})
            for msg in filteredmsg:
                self.log(level, f"{msg}", extra={'mmodule': strmodule})

            #self.log(level, f"Logged {len(filteredmsg)} Lines", extra={'mmodule': 'LOGGER'})

    # Shortcut functions for logging with custom levels
    def custom_log(self, level_name, message, module = None):
        level = level or logging.INFO
        self.mlog(level, message, module)

    def steam_output(self, message, module = None):
        self.mlog(self.levels['STEAM'], module, f"{message}")

    def building_output(self, message, module = None):
        self.mlog(self.levels['BUILDING'], module, f"{message}")

    def download_output(self, message, module = None):
        self.mlog(self.levels['DOWNLOAD'], module, f"{message}")

    def gui_console_output(self, message, module = None):
        self.mlog(self.levels['GUI_CONSOLE'], module, f"{message}")

    def debug(self, message, module = None):
        self.mlog(logging.DEBUG, module, f"{message}")

    def info(self, message, module = None):
        self.mlog(logging.INFO, module, f"{message}")

    def warning(self, message, module = None):
        self.mlog(logging.WARNING, module, f"{message}")

    def error(self, message, module = None):
        self.mlog(logging.ERROR, module, f"{message}")

    def critical(self, message, module = None):
        self.mlog(logging.CRITICAL, module, f"{message}")

    def list_levels(self):
        """Prints all available log levels including custom levels."""
        self.levels = {level: name for level, name in logging._levelToName.items() if isinstance(level, int)}
        return self.levels
