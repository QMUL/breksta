"""
Houses all logging-specific functionality.
"""

import logging


class Logger:
    """
    Encapsulate logging Singleton logic.

    Only instantiate once, use Getter to get the instance
    """
    _logger_instance: logging.Logger = None  # type: ignore
    _is_initialized: bool = False

    def __init__(self, log_level) -> None:
        self.log_level = log_level
        print("LOG_LEVEL", log_level)
        if Logger._is_initialized:
            return
            # raise Exception("Logger class already initialized")

        if Logger._logger_instance is not None:
            return
            # raise Exception("Logger class is a singleton!")

        print("once?")
        Logger._logger_instance = self._setup_logger(log_level)
        Logger._is_initialized = True

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """
        Sets up a logger for 'Breksta'. The logger writes messages
        to both the console and a log file ('file.log'), with different formats and severity levels.

        For the console, only messages with a level of WARNING or above are logged, and the format
        is: '%(name)s - %(levelname)s - %(message)s'.

        For the log file, all messages are logged and the format is:
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'.

        If the logger already has handlers set up, it returns the logger as is. This is to prevent
        adding multiple handlers to the logger if `setup_logger` is called multiple times.

        Returns:
            logging.Logger: The logger for the application.
        """
        my_app = 'Breksta'
        log_path = 'file.log'
        logger = logging.getLogger(my_app)

        # Check if the logger already has handlers. If not, add them.
        if logger.handlers:
            return logger

        # if not logger.handlers: Convert log level string to logging level
        numeric_level = getattr(logging, log_level.upper(), None)
        print(numeric_level)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {log_level}')

        logger.setLevel(level=log_level)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_path)
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger

    @classmethod
    def get_instance(cls, log_level: str = "INFO") -> logging.Logger:
        """Getter function."""
        if cls._logger_instance is None:
            cls(log_level)
        return cls._logger_instance


logger = Logger("DEBUG")
