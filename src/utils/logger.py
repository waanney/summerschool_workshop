import logging


def setup_logger(log_file="app.log"):
    """Configure the logging system."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Log to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
