#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys
from pathlib import Path

class Constants:
    def __init__(self):
        # Static values dictionary
        self._static_values = {
            "app_name": "WeMod Launcher",
            "version": "2.0.0",
            "script_name": Path("wemod.py"),
            "config_section": "Settings",
            "conf_folder_name": "wemod-launcher",
            "repo_name": "wemod-launcher",
            "repo_user": "DeckCheatz",
            "bat_start": ["start"],
            "script_cli_end": "--wemod-launcher-cli-end",
            "script_cli_start": "--wemod-launcher-cli-start",
            "allow_only_cli_end": True
        }

        # Lazy cache
        self._lazy_cache = {}

        self._logger_obj = None

    def __getattr__(self, name):
        """
        Intercept access to attributes at the class level.
        Handles static values and lazy-loaded values via generators.
        """
        # First, check if the attribute exists in the object's __dict__
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # Check if the key is a static value
            if name in self._static_values:
                return self._static_values[name]

            # Check if the value has been cached
            if name in self._lazy_cache:
                return self._lazy_cache[name]

            # If it's not cached, dynamically look for a generator method
            generator_name = f"_{name}"

            # Use object.__getattribute__ to avoid recursion
            try:
                generator_func = object.__getattribute__(self, generator_name)
                if callable(generator_func):
                    # Cache the result of the generator
                    result = generator_func()
                    self._lazy_cache[name] = result
                    return result
            except AttributeError:
                pass

            # If no generator method found, raise an AttributeError
            raise AttributeError(f"No such constant: {name}")

    def get(self, key):
        """Retrieve a value by key"""
        return self._static_values.get(key) if key in self._static_values else getattr(self, key)

    def _is_compiled(self):
        """Lazy-loaded method for checking if script is compiled"""
        return getattr(sys, "frozen", False)

    def _script_path(self):
        """
        Generator function for ScriptPath.
        """
        if self.is_compiled:
            path = Path(sys.executable).absolute()
            return path
        else:
            path = Path(__file__).parent / self.script_name
            path = path.absolute()
            for i in range(1,3):
                if path.is_file():
                    return path.absolute()
                else:
                    path = path.parent.parent / self.script_name

        # Logger can't be used here as it wound import in a loop
        raise f"Error script file ({self.script_name}) was not found"

    def _script_stem(self):
        return self.script_path.stem

    def _script_dir(self):
        return self.script_path.parent.absolute()

    def _git_base(self):
        if self.is_compiled:
            return self.script_dir.absolute()
        else:
            path = self.script_path.parent / ".git"
            for i in range(1,5):
                if path.is_dir():
                    return path.parent.absolute()
                else:
                    path = path.parent.parent / ".git"

        # Logger can't be used here as it wound import in a loop
        raise f"Error git base (.git folder) was not found"

    def _global_conf_dir(self):
        global_conf = Path.home() / ".config" / self.conf_folder_name
        global_conf.mkdir(mode=0o774, parents=True, exist_ok=True)
        return global_conf

    def _config_path(self):
        local_conf = self.script_dir / (self.script_stem + ".conf")
        if local_conf.is_file():
            return local_conf

        local_git_conf = self.git_base / (self.script_stem + ".conf")
        if local_git_conf.is_file():
            return local_git_conf

        global_conf = self.global_conf_dir / (self.script_stem + ".conf")
        return global_conf

    def _config_dir(self):
        return self.config_path.parent

    def _log_dir(self):
        logs = self.git_base / "logs"
        if self.is_compiled or not logs.is_dir():
            logs = self.global_conf_dir / "logs"
        return logs

    def _bat_file(self):
        bat = self.git_base / (self.script_stem + ".bat")
        if self.IsCompiled or not bat.is_file():
            bat = self.global_conf_dir / (self.script_stem + ".bat")

        bat.parent.mkdir(mode=0o774, parents=True, exist_ok=True)
        return bat

    def _bat_exists(self):
        return self.bat_file.exists()

    def _winetricks(self):
        tricks = self.git_base / "winetricks"
        if self.is_compiled or not tricks.is_file():
            tricks = self.global_conf_dir / "winetricks"

        tricks.parent.mkdir(mode=0o774, parents=True, exist_ok=True)
        return tricks

