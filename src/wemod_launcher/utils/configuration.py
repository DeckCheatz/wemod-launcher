#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
from consts import Constants as CN

# TODO  Change to tomllib
import configparser

# TODO  Make custom logging Module
import logging


class ConfigManagerMeta(type):
    def __getattr__(cls, name):
        """
        Intercept attribute access to dynamically fetch values from the config.

        Args:
            name (str): The configuration key to retrieve.

        Returns:
            The configuration value or raises error if not found.
        """
        cls._load_config()
        #return cls._config.get(name, None)

        # If the key exists in the config, return the value
        if name in cls._config:
            return cls._config[name]

        # If the key does not exist in the config, raise an error
        raise AttributeError(f"Config key '{name}' does not exist")


    def __setattr__(cls, name, value):
        """
        Intercept attribute assignment to modify values in the config.

        Args:
            name (str): The configuration key to set.
            value: The value to assign to the configuration key.
        """
        # Skip special attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        cls._load_config()
        cls._config[name] = str(value)  # Convert to string for consistent storage
        cls._save_config()

    def __delattr__(cls, name):
        """
        Intercept attribute deletion to remove values from the config.

        Args:
            name (str): The configuration key to delete.

        Raises:
            AttributeError: If the key does not exist in the configuration.
        """
        cls._load_config()

        if name not in cls._config:
            raise AttributeError(f"Config key '{name}' does not exist")

        del cls._config[name]
        cls._save_config()

class ConfigManager(metaclass=ConfigManagerMeta):
    # Static variable to store configuration data
    _config = None

    @classmethod
    def _load_config(cls, config_file=CT.ConfigPath):
        """
        Load the configuration from an conf file.

        Args:
            config_file (str, optional): Path to the configuration file.
                                         Defaults to CT.ConfigPath.
        """
        # Ensure the configuration file exists
        if not os.path.exists(config_file):
            try:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                # Create an empty configuration file
                with open(config_file, 'w') as f:
                    pass
            except OSError as e:
                logging.error(f"Error creating config file: {e}")
                return

        config = configparser.ConfigParser()
        config.read(config_file)

        # Initialize _config if it's None
        if cls._config is None:
            cls._config = {}

        # Load all options from the CT.ConfigSection section
        if CT.ConfigSection in config:
            cls._config.update({
                key: config[CT.ConfigSection].get(key)
                for key in config[CT.ConfigSection]
            })

    @classmethod
    def _save_config(cls, config_file=CT.ConfigPath):
        """
        Save the current configuration to an conf file.

        Args:
            config_file (str, optional): Path to the configuration file.
                                         Defaults to CT.ConfigPath.
        """
        try:
            config = configparser.ConfigParser()

            # Ensure the CT.ConfigSection section exists
            if CT.ConfigSection not in config:
                config.add_section(CT.ConfigSection)

            # Set all config values in the CT.ConfigSection section
            for key, value in cls._config.items():
                config.set(CT.ConfigSection, key, str(value))

            with open(config_file, "w") as configfile:
                config.write(configfile)
        except IOError as e:
            logging.error(f"Error saving config file: {e}")
