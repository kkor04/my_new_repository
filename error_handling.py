import logging

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger("ErrorHandler")
        logging.basicConfig(level=logging.ERROR)

    def handle_error(self, error: Exception, context: str = ""):
        """Log and handle an error."""
        self.logger.error(f"Error in {context}: {str(error)}")
        print(f"[ERROR] {context}: {str(error)}")
