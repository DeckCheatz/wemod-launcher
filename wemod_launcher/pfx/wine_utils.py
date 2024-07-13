from pathlib import Path, PureWindowsPath, PurePosixPath, WindowsPath


class WineUtils:
    @staticmethod
    def native_path(path: str) -> PureWindowsPath | PurePosixPath:
        if path.startswith("C:") or path.startswith("Z:"):
            return PureWindowsPath(path)

        return PurePosixPath(path)
