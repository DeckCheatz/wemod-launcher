#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import sys
from pathlib import Path

class ConstantsMeta(type):
    def __getattr__(cls, name):
        """
        Intercept access to attributes at the class level.
        Handles static values and lazy-loaded values via generators.
        """
        # Check if the key is a static value
        if name in cls._static_values:
            return cls._static_values[name]

        # Check if the value has been cached
        if name in cls._lazy_cache:
            return cls._lazy_cache[name]

        # If it's not cached, dynamically look for a generator method
        generator_name = f"_{name}"
        if hasattr(cls, generator_name):
            generator_func = getattr(cls, generator_name)
            if callable(generator_func):
                # Cache the result of the generator
                cls._lazy_cache[name] = generator_func()
                return cls._lazy_cache[name]

        raise AttributeError(f"No such constant: {name}")

class Constants(metaclass=ConstantsMeta):
    _static_values = {
        "AppName": "WeMod Launcher",
        "Version": "2.0.0",
        "ScriptName": Path("wemod.py"),
        "ConfigSection": "Settings",
        "RepoName" : "wemod-launcher",
        "RepoUser": "DeckCheatz",
        "BatStart": ["start"]
    }

    _lazy_cache = {}

    @classmethod
    def get(cls, key):
        """
        Get a value either from static values, cache, or dynamic generation.
        """
        # Try static values first
        if key in cls._static_values:
            return cls._static_values[key]

        # Then try cached values
        if key in cls._lazy_cache:
            return cls._lazy_cache[key]

        # If not cached, use the generator method if it exists
        generator_name = f"_{key}"
        if hasattr(cls, generator_name):
            generator_func = getattr(cls, generator_name)
            if callable(generator_func):
                cls._lazy_cache[key] = generator_func()  # Cache the value
                return cls._lazy_cache[key]

        raise AttributeError(f"No such constant: {key}")

    @classmethod
    def _IsCompiled(cls):
        return getattr(sys, "frozen", False)

    @classmethod
    def _ScriptPath(cls):
        """
        Generator function for ScriptPath.
        """
        if cls.IsCompiled:
            path = Path(sys.executable).absolute()
            return path
        else:
            path = Path(__file__).parent / cls.ScriptName
            path = path.absolute()
            for range(1,3):
                if path.is_file():
                    return path.absolute()
                else:
                    path = path.parent.parent / cls.ScriptName
        raise f"Error script file ({cls.ScriptName}) was not found"

    @classmethod
    def _ScriptStem(cls):
        return cls.ScriptPath.stem


    @classmethod
    def _ScriptDir(cls):
        return cls.ScriptPath.parent.absolute()

    @classmethod
    def _GitBase(cls):
        if cls.IsCompiled:
            return cls.ScriptDir.absolute()
        else:
            path = cls.ScriptPath.parent / ".git"
            for range(1,5):
                if path.is_dir():
                    return path.parent.absolute()
                else:
                    path = path.parent.parent / ".git"
        return "Error git base (.git folder) was not found"

    @classmethod
    def _GlobalConfDir(cls):
        global_conf = Path.home() / ".config" / cls.RepoName
        global_conf.mkdir(mode=0o664, parents=True, exist_ok=True)
        return global_conf

    @classmethod
    def _ConfigPath(cls):
        local_conf = cls.ScriptDir / (cls.ScriptStem + ".conf")
        if local_conf.is_file():
            return local_conf

        local_git_conf = cls.GitBase / (cls.ScriptStem + ".conf")
        if not conf and local_git_conf.is_file():
            return local_git_conf

        global_conf = cls.GlobalConfDir / (cls.ScriptStem + ".conf")
        return global_conf

    @classmethod
    def _ConfigDir(cls):
        return cls.ConfigPath.parent

    @classmethod
    def _LogPath(cls):
        return = Path("logs")

    @classmethod
    def _BatFile(cls):
        bat = cls.GitBase / (cls.ScriptStem + ".bat")
        if cls.IsCompiled and not bat.exists():
            bat = cls.GlobalConfDir / (cls.ScriptStem + ".bat")

        bat.parent.mkdir(mode=0o664, parents=True, exist_ok=True)
        return bat

    @classmethod
    def _BatExists(cls):
        return cls.BatFile.exists()

    @classmethod
    def _WineTricks(cls):
        tricks = cls.GitBase / "winetricks"
        if cls.IsCompiled and not tricks.exists():
            tricks = cls.GlobalConfDir / "winetricks"

        tricks.parent.mkdir(mode=0o664, parents=True, exist_ok=True)
        return tricks


