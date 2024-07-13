from pathlib import Path, PureWindowsPath, PurePosixPath, WindowsPath


class WineUtils:
    @staticmethod
    def native_path(path: str) -> PureWindowsPath | PurePosixPath:
        if "C:" in path or "Z:" in path:
            return PureWindowsPath(path)

        return PurePosixPath(path)
