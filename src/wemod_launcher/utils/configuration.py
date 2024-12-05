#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys
from consts import Constants
import configparser

CT = None
CT = Constants()

class ConfigManager:
    def __init__(self, env_vars=False, cmd=False, config_file=None):
        # Use super().__setattr__ to set initial attributes
        super().__setattr__('_env_vars', env_vars)
        super().__setattr__('_cmd', cmd)
        super().__setattr__('_config', {})
        super().__setattr__('_config_file', config_file or CT.config_path)
        super().__setattr__('_logger_obj', None)
        super().__setattr__('AppArgs', [])
        super().__setattr__('PassArgs', [])
        if cmd:
            self._args_grabber()

    def __getattr__(self, name):
        """
        Dynamically fetch values from the config or environment.
        """
        # Use getattr to safely access attributes
        env_vars = getattr(self, '_env_vars')

        if env_vars:
            if name in os.environ:
                return os.environ[name]

        self._load_config()
        cmd = getattr(self, '_cmd')

        if cmd:
            app_args = getattr(self, 'AppArgs')
            for arg in app_args:
                s, e = arg.split("=", 1)
                s = s.strip()
                if s == name:
                    return e.strip()

        # If the key exists in the config, return the value
        config = getattr(self, '_config')
        if name in config:
            return config[name]

        # If the key does not exist in the config, return None
        return None

    def __setattr__(self, name, value):
        """
        Modify values in the config or environment.
        """
        # Use getattr to safely access attributes
        env_vars = getattr(self, '_env_vars', False)

        if env_vars:
            os.environ[name] = str(value)
            return

        # Use super().__setattr__ for special attributes
        if name.startswith('_') or name in ['AppArgs', 'PassArgs']:
            super().__setattr__(name, value)
            return

        self._load_config()
        config = getattr(self, '_config')
        config[name] = str(value)  # Convert to string for consistent storage
        self._save_config()

    def __delattr__(self, name):
        """
        Remove values from the config or environment.
        """
        # Use getattr to safely access attributes
        env_vars = getattr(self, '_env_vars', False)

        if env_vars:
            if name in os.environ:
                del os.environ[name]
                return

        self._load_config()
        config = getattr(self, '_config')

        if name not in config:
            # You might want to replace this with proper logging
            print(f"ERROR: Config key '{name}' does not exist")
            return

        del config[name]
        self._save_config()

    def _load_config(self, config_file=None):
        """
        Load the configuration from a config file.
        """
        config_file = config_file or self._config_file

        # Ensure the configuration file exists
        if not os.path.exists(config_file):
            try:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                # Create an empty configuration file
                with open(config_file, 'w') as f:
                    pass
            except OSError as e:
                return

        config = configparser.ConfigParser()
        config.read(config_file)

        # Load all options from the CT.config_section section
        if CT.config_section in config:
            self._config.update({
                key: config[CT.config_section].get(key)
                for key in config[CT.config_section]
            })

    def _save_config(self, config_file=None):
        """
        Save the current configuration to a config file.
        """
        config_file = config_file or self._config_file
        try:
            config = configparser.ConfigParser()

            # Ensure the CT.config_section section exists
            if CT.config_section not in config:
                config.add_section(CT.config_section)

            # Set all config values in the CT.config_section section
            for key, value in self._config.items():
                config.set(CT.config_section, key, str(value))

            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as configfile:
                config.write(configfile)
        except IOError as e:
            # Logger can't be used here as it wound import in a loop
            raise f"Error saving config file: {e}"

    def _args_grabber(self, args=sys.argv):
        arguments = sys.argv[1:]
        End = self.script_cli_end or CT.script_cli_end
        Start = self.script_cli_start or CT.script_cli_start
        AllowOnlyEnd = self.allow_only_cli_end or CT.allow_only_cli_end
        EndIn = bool(End in arguments)
        if EndIn and Start in arguments:
            e = arguments.index(End)
            s = arguments.index(Start) + 1
            if e > s+1:
                self.AppArgs = arguments[s:e]
                self.PassArgs = arguments[:s-1]
                self.PassArgs += arguments[:e+1]
            else:
                arguments.remove(End)
                arguments.remove(Start)
                self.PassArgs = arguments
                return
        elif AllowOnlyEnd and End in arguments:
            e = arguments.index(End)
            if e > 0:
                self.AppArgs = arguments[:e]
                self.PassArgs = arguments[e+1:]
            else:
                self.PassArgs = arguments[1:]



