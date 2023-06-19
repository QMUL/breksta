# logger_config.py

import logging

def setup_logger():
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
