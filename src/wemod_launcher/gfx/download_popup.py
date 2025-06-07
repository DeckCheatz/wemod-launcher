from xdg.BaseDirectory import save_cache_path
import FreeSimpleGUI as sg
import requests
import os
import threading
from pathlib import Path
import signal
import json # To store timestamp information

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
        self.__download_thread = None
        self.__cancel_event = threading.Event()
        self.__status_message = ""
        # New: Use a more robust system for outcome
        self.__download_outcome = None # Can be 'success', 'cancelled', 'failed'

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

    def __download(self, window):
        self.__logger.debug("Starting download...")
        window.write_event_value("-STATUS_UPDATE-", "Starting download...")
        window.write_event_value("-SET_BUTTON_STATE-", {"retry_visible": False, "cancel_enabled": True})
        
        try:
            headers = {}
            local_timestamp = self.__get_cached_timestamp()

            if self.__filename.exists() and local_timestamp:
                # Check if the local file's timestamp matches the remote's
                head_response = requests.head(self.__dl_uri, allow_redirects=True)
                head_response.raise_for_status()
                remote_timestamp = head_response.headers.get("Last-Modified")
                
                if remote_timestamp == local_timestamp:
                    self.__logger.info("File already up-to-date. Skipping download.")
                    window.write_event_value("-PROGRESS-", 100)
                    window.write_event_value("-DOWNLOAD COMPLETE-", f"File '{self.__filename.name}' is already up-to-date!")
                    self.__download_outcome = 'success' # Mark outcome
                    return
                else:
                    self.__logger.info("Remote file is newer, re-downloading.")

            response = requests.get(self.__dl_uri, stream=True, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            total_size = int(response.headers.get("content-length", 0))
            remote_timestamp = response.headers.get("Last-Modified")
            downloaded_size = 0

            with open(self.__filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.__cancel_event.is_set():
                        # Signal the main thread that the download was cancelled
                        window.write_event_value("-DOWNLOAD ERROR-", "Download cancelled by user.")
                        self.__download_outcome = 'cancelled' # Mark outcome
                        return # Exit the download thread
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress = (
                        (downloaded_size / total_size) * 100
                        if total_size > 0
                        else 0
                    )
                    window.write_event_value("-PROGRESS-", progress)
            
            if remote_timestamp:
                self.__save_cached_timestamp(remote_timestamp)

            window.write_event_value("-DOWNLOAD COMPLETE-", f"Download of {self.__filename.name} complete!")
            self.__download_outcome = 'success' # Mark outcome

        except requests.exceptions.RequestException as e:
            self.__logger.error(f"Download error: {e}")
            window.write_event_value("-DOWNLOAD ERROR-", f"Download error: {e}")
            self.__download_outcome = 'failed' # Mark outcome
        except Exception as e:
            self.__logger.error(f"Error during download: {e}")
            window.write_event_value("-DOWNLOAD ERROR-", f"Error: {e}")
            self.__download_outcome = 'failed' # Mark outcome
        finally:
            window.write_event_value("-DOWNLOAD_FINISHED-", None) # Signal that the download thread has finished

    def __signal_handler(self, sig, frame):
        self.__logger.info("Ctrl-C detected. Attempting to cancel download.")
        self.__cancel_event.set()
        # The main loop will now handle the outcome and window closure.

    def run(self) -> Path | str: # Type hint for the return value
        # Register the signal handler for Ctrl-C
        signal.signal(signal.SIGINT, self.__signal_handler)

        layout = [
            [sg.Text("Downloading asset:", size=(30, 1)), sg.Text(self.__filename.name, size=(30, 1), key="-FILENAME-")],
            [sg.ProgressBar(100, orientation="h", size=(40, 20), key="-PROGRESS_BAR-")],
            [sg.Text("Status:", size=(8, 1)), sg.Text("", size=(50, 1), key="-STATUS-")],
            [sg.Button("Cancel", key="-CANCEL-", disabled=False), sg.Button("Retry", key="-RETRY-", disabled=True, visible=False)],
        ]

        # Use (None, None) for FreeSimpleGUI to attempt intelligent centering,
        # which often corresponds to the primary/focused monitor in most setups.
        window = sg.Window("Asset Downloader", layout, finalize=True, location=(None, None))

        # Start download immediately
        self.__download_outcome = None # Reset outcome for a new run
        self.__cancel_event.clear()
        self.__download_thread = threading.Thread(
            target=self.__download,
            args=(window,),
            daemon=True,
        )
        self.__download_thread.start()

        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                self.__cancel_event.set() # Signal cancellation to the thread
                # Do NOT break immediately, let the thread finish signaling its outcome
                pass # Continue loop to process final events from the thread
            elif event == "-CANCEL-":
                self.__cancel_event.set()
                window["-STATUS-"].update("Cancelling download...")
                window["-CANCEL-"].update(disabled=True)
                window["-RETRY-"].update(disabled=True, visible=False)
            elif event == "-RETRY-":
                window["-PROGRESS_BAR-"].update(0)
                window["-STATUS-"].update("Retrying download...")
                window["-CANCEL-"].update(disabled=False)
                window["-RETRY-"].update(disabled=True, visible=False)
                self.__cancel_event.clear()
                self.__download_thread = threading.Thread(
                    target=self.__download,
                    args=(window,),
                    daemon=True,
                )
                self.__download_thread.start()
            elif event == "-PROGRESS-":
                progress = values[event]
                window["-PROGRESS_BAR-"].update(progress)
                window["-STATUS-"].update(f"Downloading: {progress:.2f}%")
            elif event == "-STATUS_UPDATE-":
                window["-STATUS-"].update(values[event])
            elif event == "-SET_BUTTON_STATE-":
                window["-RETRY-"].update(visible=values[event]["retry_visible"])
                window["-CANCEL-"].update(disabled=not values[event]["cancel_enabled"])
            elif event == "-DOWNLOAD COMPLETE-":
                message = values[event]
                window["-STATUS-"].update(message)
                window["-CANCEL-"].update(disabled=True)
                window["-RETRY-"].update(disabled=True, visible=False)
                sg.popup_ok("Download Complete!", title="Success")
                window.close() # Close window after success popup
                break # Exit the event loop
            elif event == "-DOWNLOAD ERROR-":
                error_message = values[event]
                window["-STATUS-"].update(error_message)
                window["-CANCEL-"].update(disabled=True)
                window["-RETRY-"].update(disabled=False, visible=True)
                
                if "cancelled by user" in error_message.lower():
                    # No popup for explicit cancellation from thread, just update status
                    pass # Outcome already set in __download
                else:
                    sg.popup_error("Download Failed", error_message)
                
                # We don't break here immediately, as we wait for -DOWNLOAD_FINISHED-
                # which will trigger the final state and window close if applicable.
                pass 
            
            elif event == "-DOWNLOAD_FINISHED-":
                # This event is triggered by the download thread when it finishes (success, error, or internal cancel)
                # Ensure buttons are in appropriate state
                if self.__download_outcome == 'success':
                    # Already handled by -DOWNLOAD COMPLETE- which closes the window
                    pass
                elif self.__download_outcome == 'cancelled':
                    # Explicitly handle cancellation here
                    sg.popup_ok("Download cancelled by user.", title="Cancelled")
                    window.close() # Close window after cancel popup
                    break # Exit the event loop
                elif self.__download_outcome == 'failed':
                    # An error occurred and was not explicitly cancelled by user from UI
                    # If sg.popup_error was already shown, just ensure window closes.
                    if not window.is_closed(): # Only close if not already closed by a previous popup (e.g. success)
                        window.close()
                    break # Exit the event loop as download is truly finished with a failure
                else: # Fallback for unexpected states, or just general cleanup
                    window["-CANCEL-"].update(disabled=True)
                    window["-RETRY-"].update(disabled=True, visible=False)
                    if not window.is_closed(): # Ensure window is closed if it wasn't by specific outcomes
                        window.close()
                    break # Exit the event loop if the download thread has truly finished its work and reported
        
        # Clean up the thread
        if self.__download_thread and self.__download_thread.is_alive():
            self.__cancel_event.set()
            self.__download_thread.join(timeout=2) # Give it time to react to cancellation

        # The window is already closed by this point if it reached success, failure, or explicit cancellation.
        # This final check ensures it's closed in all scenarios, especially if WIN_CLOSED was the trigger
        # and no other specific outcome event fully processed.
        if window and not window.is_closed():
             window.close()

        # Determine the final return value based on the download outcome
        if self.__download_outcome == 'success':
            return self.__filename
        elif self.__download_outcome == 'cancelled':
            return "cancelled" # Explicit string for cancellation
        elif self.__download_outcome == 'failed':
            return "failed" # Explicit string for failure
        else:
            # Fallback for unexpected termination (e.g., window forcefully closed,
            # or program exited before a clear outcome was set). Treat as failed or
            # a general non-success state.
            self.__logger.warning("Download process ended without a clear success, cancelled, or failed outcome.")
            return "failed" # Default to 'failed' for ambiguous non-success states
