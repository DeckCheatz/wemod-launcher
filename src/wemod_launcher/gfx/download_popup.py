from xdg.BaseDirectory import save_cache_path
import requests
import os
import threading
from pathlib import Path
import signal
import json
import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QCloseEvent

# Assuming utils.logger is available and correctly configured
from ..utils.logger import LoggingHandler

class DownloadCancelledByUserException(Exception):
    """Custom exception raised when the user explicitly cancels the download process.
    This is primarily for internal thread communication, not for the run() method's final return.
    """
    pass

class DownloadPopupGfx(object):
    def __init__(self, filename: str, dl_uri: str):
        self.__logger = LoggingHandler(__name__).get_logger()

        self.__filename = Path(save_cache_path("wemod_launcher")) / f"assets/{filename}"
        self.__timestamp_file = self.__filename.with_suffix(".timestamp")
        self.__dl_uri = dl_uri

        if not self.__filename.parent.exists():
            self.__filename.parent.mkdir(parents=True, exist_ok=True)

        self.__logger.debug("DownloadPopupGfx initialized")

    def __get_cached_timestamp(self) -> str | None:
        """Reads the cached Last-Modified timestamp."""
        if self.__timestamp_file.exists():
            try:
                with open(self.__timestamp_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_modified")
            except json.JSONDecodeError:
                self.__logger.warning(f"Could not decode JSON from {self.__timestamp_file}")
                return None
        return None

    def __save_cached_timestamp(self, timestamp: str):
        """Saves the Last-Modified timestamp to a cache file."""
        with open(self.__timestamp_file, "w") as f:
            json.dump({"last_modified": timestamp}, f)

    def run(self) -> Path | str:
        """Display the download dialog and handle the download process."""
        try:
            # Create QApplication if it doesn't exist
            app = QApplication.instance()
            if app is None:
                self.__logger.debug("Creating new QApplication instance")
                app = QApplication(sys.argv)
                
                # Set application properties
                app.setApplicationName("WeMod Launcher")
                app.setApplicationVersion("1.503")
                
            # Check if we have a valid display
            if not app.primaryScreen():
                self.__logger.error("No display/screen available for Qt application")
                return "No display available - cannot show GUI"
            
            # Show dialog
            self.__logger.debug("Creating download dialog")
            dialog = DownloadDialog(self.__filename.name)
            dialog.start_download(self)
            
            self.__logger.debug("Executing dialog")
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                self.__logger.info(f"Download completed successfully: {self.__filename}")
                return self.__filename
            elif result == QDialog.DialogCode.Rejected:
                self.__logger.info("Download was cancelled by user")
                return "Download cancelled by user"
            else:
                self.__logger.warning("Download dialog closed with unknown result")
                return "Download cancelled or failed"
                
        except Exception as e:
            self.__logger.error(f"Error in Qt GUI: {e}")
            return f"GUI Error: {e}"

    def __download_with_signals(self, worker):
        """Download method that emits signals for Qt worker thread."""
        try:
            worker.status_updated.emit("Checking for cached file...")
            
            # Check if file exists and get timestamp
            local_timestamp = self.__get_cached_timestamp()
            headers = {}
            if local_timestamp:
                headers["If-Modified-Since"] = local_timestamp

            worker.status_updated.emit("Contacting server...")
            response = requests.head(self.__dl_uri, headers=headers)

            if response.status_code == 304:
                # File hasn't changed
                worker.status_updated.emit("File is up-to-date!")
                worker.download_finished.emit(True, f"File '{self.__filename.name}' is already up-to-date!")
                return

            # Download the file
            worker.status_updated.emit("Starting download...")
            response = requests.get(self.__dl_uri, stream=True, headers=headers)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(self.__filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if worker.cancelled:
                        worker.status_updated.emit("Download cancelled")
                        worker.download_finished.emit(False, "Download cancelled by user")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            worker.progress_updated.emit(progress)
                            worker.status_updated.emit(f"Downloaded {downloaded:,} / {total_size:,} bytes")

            # Save timestamp
            last_modified = response.headers.get("Last-Modified")
            if last_modified:
                self.__save_cached_timestamp(last_modified)

            worker.status_updated.emit("Download completed!")
            worker.download_finished.emit(True, "Download completed successfully!")

        except requests.exceptions.RequestException as e:
            worker.status_updated.emit(f"Network error: {e}")
            worker.download_finished.emit(False, f"Network error: {e}")
        except Exception as e:
            worker.status_updated.emit(f"Error: {e}")
            worker.download_finished.emit(False, f"Error: {e}")

class DownloadWorker(QThread):
    """Worker thread for downloading files with progress updates."""
    
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)   # Status message
    download_finished = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, download_popup, parent=None):
        super().__init__(parent)
        self.download_popup = download_popup
        self.cancelled = False
        
    def cancel(self):
        """Cancel the download."""
        self.cancelled = True
        
    def run(self):
        """Run the download in the background thread."""
        try:
            self.download_popup._DownloadPopupGfx__download_with_signals(self)
        except Exception as e:
            self.download_finished.emit(False, str(e))


class DownloadDialog(QDialog):
    """Qt-based download progress dialog."""
    
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asset Downloader")
        self.setModal(True)
        self.setFixedSize(500, 200)
        
        # Center the dialog on screen
        self.move(
            QApplication.primaryScreen().geometry().center() - self.rect().center()
        )
        
        self.filename = filename
        self.download_worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Filename label
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("Downloading asset:"))
        self.filename_label = QLabel(self.filename)
        self.filename_label.setStyleSheet("font-weight: bold;")
        filename_layout.addWidget(self.filename_label)
        filename_layout.addStretch()
        layout.addLayout(filename_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        
        self.retry_button = QPushButton("Retry")
        self.retry_button.clicked.connect(self.retry_download)
        self.retry_button.setVisible(False)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.retry_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def start_download(self, download_popup):
        """Start the download process."""
        self.download_worker = DownloadWorker(download_popup, self)
        self.download_worker.progress_updated.connect(self.update_progress)
        self.download_worker.status_updated.connect(self.update_status)
        self.download_worker.download_finished.connect(self.download_completed)
        self.download_worker.start()
        
    def update_progress(self, percentage):
        """Update the progress bar."""
        self.progress_bar.setValue(percentage)
        
    def update_status(self, message):
        """Update the status label."""
        self.status_label.setText(message)
        
    def cancel_download(self):
        """Cancel the current download."""
        if self.cancel_button.text() == "Close":
            # Dialog is showing error state, just close it
            self.reject()
            return
            
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.update_status("Cancelling download...")
            self.cancel_button.setEnabled(False)
            
            # Wait briefly for the worker to cancel, then close dialog
            QTimer.singleShot(500, self.reject)  # Close dialog after 500ms
        else:
            # No download running, just close the dialog
            self.reject()
            
    def retry_download(self):
        """Retry the download."""
        self.retry_button.setVisible(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        # The download_popup will restart the download
        
    def download_completed(self, success, message):
        """Handle download completion."""
        if success:
            self.update_status("Download completed successfully!")
            QTimer.singleShot(1000, self.accept)  # Close after 1 second
        else:
            # Check if this was a user cancellation
            if "cancelled" in message.lower():
                self.update_status("Download cancelled by user")
                QTimer.singleShot(500, self.reject)  # Close dialog with rejection
            else:
                # This was an error, show retry option
                self.update_status(f"Download failed: {message}")
                self.cancel_button.setText("Close")
                self.cancel_button.setEnabled(True)
                self.retry_button.setVisible(True)
            
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        if self.download_worker and self.download_worker.isRunning():
            self.cancel_download()
            self.download_worker.wait(3000)  # Wait up to 3 seconds
        event.accept()
