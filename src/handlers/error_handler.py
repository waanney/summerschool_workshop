from ..utils.logger import setup_logger

class ErrorHandler:
    def __init__(self, log_file="app.log"):
        self.logger = setup_logger(log_file)

    def handle_exception(self, exception: Exception):
        """Handle exceptions and log them."""
        exception_type = type(exception).__name__
        self.logger.error(f"{exception_type}: {str(exception)}")
        return f"An error occurred: {exception_type}. Please try again later."
