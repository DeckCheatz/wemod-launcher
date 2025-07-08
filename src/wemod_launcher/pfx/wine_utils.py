import re
from pathlib import PureWindowsPath, PurePosixPath, PurePath


class WineUtils:
    @staticmethod
    def native_path(path: str) -> PureWindowsPath | PurePosixPath:
        # Match any Windows drive letter pattern like C:\ or D:/ etc.
        if re.match(r"^[a-zA-Z]:[\\/]", path):
            return PureWindowsPath(path)

        return PurePosixPath(path)

    @staticmethod
    def is_windows_path(path: PurePath) -> bool:
        return isinstance(path, PureWindowsPath)

    @staticmethod
    def is_posix_path(path: PurePath) -> bool:
        return isinstance(path, PurePosixPath)
