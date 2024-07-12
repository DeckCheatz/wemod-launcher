from .utils.logger import LoggingHandler

log = LoggingHandler(__name__).get_logger()

def main():
    log.info("Welcome to WeMod Launcher!")
    pass
