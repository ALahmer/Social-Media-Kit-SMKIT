import logging
from colorlog import ColoredFormatter


class LoggerSetup:
    def __init__(self, level=logging.INFO):
        self.level = level
        self.configure_logger()

    def configure_logger(self):

        # Define a color format
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        # Set up the logger with the custom handler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(self.level)

        logging.debug("Logging is configured successfully.")
