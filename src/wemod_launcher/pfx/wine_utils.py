import re
from pathlib import PureWindowsPath, PurePosixPath


class WineUtils:
    @staticmethod
    def native_path(path: str) -> PureWindowsPath | PurePosixPath:
        # Match any Windows drive letter pattern like C:\ or D:/ etc.
        if re.match(r"^[a-zA-Z]:[\\/]", path):
            return PureWindowsPath(path)

        return PurePosixPath(path)
