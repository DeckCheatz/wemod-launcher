import click
import sys
from wemod_launcher.utils.logger import LoggingHandler
from wemod_launcher.utils.configuration import Configuration
from wemod_launcher.utils.consts import Consts

log = LoggingHandler(__name__).get_logger()
cfg = Configuration()
consts = Consts()


@click.command()
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--no-gui', is_flag=True, help='Run in command-line mode only')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(version, no_gui, debug):
    """WeMod Launcher - Tool to launch WeMod with games on Steam Deck/Linux.
    
    This tool provides a GUI interface for launching WeMod with games.
    Run without arguments to start the graphical interface.
    """
    if debug:
        log.setLevel('DEBUG')
        log.debug("Debug logging enabled")
    
    if version:
        click.echo("WeMod Launcher v1.503")
        click.echo("Qt6-based GUI for Steam Deck compatibility")
        return

    if no_gui:
        click.echo("Command-line mode not yet implemented")
        click.echo("Please run without --no-gui to use the graphical interface")
        return

    log.info("Welcome to WeMod Launcher!")

    # Only import and use Qt components when needed for GUI
    try:
        # Check if we have a display available
        import os
        if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            if os.environ.get('XDG_SESSION_TYPE') != 'tty':
                log.warning("No display detected, setting Qt platform to offscreen")
                os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from wemod_launcher.gfx.welcome_screen import WelcomeScreenGfx
        WelcomeScreenGfx().run()
        from wemod_launcher.gfx.download_popup import DownloadPopupGfx
        dl = DownloadPopupGfx("dotnet48.exe", "https://download.visualstudio.microsoft.com/download/pr/2d6bb6b2-226a-4baa-bdec-798822606ff1/8494001c276a4b96804cde7829c04d7f/ndp48-x86-x64-allos-enu.exe")
        result = dl.run()
        log.info(f"Download result: {result}")

    except ImportError as e:
        log.error(f"Failed to import Qt components: {e}")
        click.echo("Error: Qt6 components not available. Please install PyQt6.")
        sys.exit(1)
    except Exception as e:
        log.error(f"Failed to start GUI: {e}")
        log.debug(f"Exception details: {type(e).__name__}: {e}")
        click.echo(f"Error: Failed to start graphical interface: {e}")
        click.echo("Try setting QT_QPA_PLATFORM=offscreen or ensure X11/Wayland is available")
        sys.exit(1)


if __name__ == "__main__":
    main()
