from xdg.BaseDirectory import save_cache_path
import requests
from pathlib import Path
import json
import threading
import signal
import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

# Assuming utils.logger is available and correctly configured
from ..utils.logger import LoggingHandler


class WelcomeScreenDialog(QDialog):
    """Qt-based welcome screen dialog."""
    
    WINDOW_TITLE = "WeMod Launcher Setup"
    WELCOME_MESSAGE = "Welcome to the WeMod Installer!\nPress OK to start the setup."
    
    def __init__(self, logo_pixmap=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # Center the dialog on screen
        self.move(
            QApplication.primaryScreen().geometry().center() - self.rect().center()
        )
        
        self.setup_ui(logo_pixmap)
        
    def setup_ui(self, logo_pixmap):
        """Set up the UI elements."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo
        if logo_pixmap and not logo_pixmap.isNull():
            logo_label = QLabel()
            # Scale logo to reasonable size while maintaining aspect ratio
            scaled_pixmap = logo_pixmap.scaled(
                64, 64, Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)
        
        # Welcome message
        message_label = QLabel(self.WELCOME_MESSAGE)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; margin: 20px 0px;")
        layout.addWidget(message_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)


class WelcomeScreenGfx(object):
    WEMOD_LOGO_URL: str = (
        "https://www.wemod.com/static/images/device-icons/favicon-192-ce0bc030f3.png"
    )

    def __init__(self):
        self.__logger = LoggingHandler(__name__).get_logger()

        self.__cache_path = (
            Path(save_cache_path("wemod_launcher")) / "assets/wemod_logo.png"
        )
        self.__timestamp_file = self.__cache_path.with_suffix(".timestamp")
        
        self.__logo_raw = None
        # Don't prepare logo until run() is called to avoid Qt issues

        self.__logger.debug("WelcomeScreenGfx initialized")

    def __get_cached_timestamp(self) -> str | None:
        """Reads the cached Last-Modified timestamp."""
        if self.__timestamp_file.exists():
            try:
                with open(self.__timestamp_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_modified")
            except json.JSONDecodeError:
                self.__logger.warning("Invalid timestamp file, will re-download")
        return None

    def __save_cached_timestamp(self, timestamp: str):
        """Saves the Last-Modified timestamp to a cache file."""
        with open(self.__timestamp_file, "w") as f:
            json.dump({"last_modified": timestamp}, f)

    def __prepare_logo(self):
        """Prepare the WeMod logo for display."""
        if self.__cache_path.exists():
            self.__logger.debug("Loading logo from cache")
            with open(str(self.__cache_path), "rb") as f:
                self.__logo_raw = f.read()
                
            # Check if we need to update the cached logo
            local_timestamp = self.__get_cached_timestamp()
            if local_timestamp:
                try:
                    headers = {"If-Modified-Since": local_timestamp}
                    response = requests.head(self.WEMOD_LOGO_URL, headers=headers)
                    if response.status_code == 304:
                        self.__logger.debug("Logo is up to date")
                        return
                    elif response.status_code == 200:
                        self.__logger.debug("Logo has been updated, downloading new version")
                        self.__download_and_cache_logo()
                except requests.exceptions.RequestException as e:
                    self.__logger.warning(f"Failed to check logo freshness: {e}")
                    # Continue with cached version
        else:
            self.__download_and_cache_logo()

    def __download_and_cache_logo(self):
        """Download and cache the logo with timestamp tracking."""
        self.__cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.__logger.debug("Downloading logo to cache, and memory.")
        try:
            response = requests.get(self.WEMOD_LOGO_URL, stream=False)
            response.raise_for_status()
            
            logo_raw = response.content
            with open(str(self.__cache_path), "wb") as f:
                f.write(logo_raw)
            with open(str(self.__cache_path), "rb") as f:
                self.__logo_raw = f.read()
                
            # Save timestamp if available
            last_modified = response.headers.get("Last-Modified")
            if last_modified:
                self.__save_cached_timestamp(last_modified)
                
        except requests.exceptions.RequestException as e:
            self.__logger.error(f"Failed to download logo: {e}")
            self.__logo_raw = None

    def run(self) -> bool:
        """Display the welcome screen and return user's choice."""
        # Prepare logo now that Qt is about to be initialized
        self.__prepare_logo()
        
        # Ensure proper Qt initialization
        import os
        
        # Set Qt platform plugin path if not set
        if 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
            # Try to find Qt plugins in common locations
            possible_paths = [
                '/usr/lib/qt6/plugins/platforms',
                '/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms',
                '/usr/lib64/qt6/plugins/platforms',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.dirname(path)
                    break
        
        # Set a fallback platform if no display is available
        if 'DISPLAY' not in os.environ and 'WAYLAND_DISPLAY' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            # Use sys.argv for proper argument handling
            app = QApplication(sys.argv)
            # Set application properties
            app.setApplicationName("WeMod Launcher")
            app.setApplicationVersion("1.503")
            app.setOrganizationName("DeckCheatz")
        
        # Create logo pixmap if available
        logo_pixmap = None
        if self.__logo_raw:
            logo_pixmap = QPixmap()
            logo_pixmap.loadFromData(self.__logo_raw)
        
        # Show dialog and get result
        dialog = WelcomeScreenDialog(logo_pixmap)
        result = dialog.exec()
        
        return result == QDialog.DialogCode.Accepted
