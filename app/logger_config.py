"""
Houses all logging-specific functionality.
"""

import logging


def setup_logger() -> logging.Logger:
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
    logger = logging.getLogger(my_app)

    # Check if the logger already has handlers. If not, add them.
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('file.log')
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
