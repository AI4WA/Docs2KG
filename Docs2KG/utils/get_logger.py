import logging
import sys


def get_logger(name) -> logging.Logger:
    """
    Get a logger object with the given name

    Args:
        name (str): Name of the logger

    Returns:
        logging.Logger: Logger object

    """
    # Create a logger
    the_logger = logging.getLogger(name)
    the_logger.setLevel(logging.INFO)

    # Create console handler and set level to debug
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create formatter, start with file name and line of code (line number) that issued the log statement
    formatter = logging.Formatter(
        "%(asctime)s|%(filename)s|Line: %(lineno)d -- %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to the_logger
    the_logger.addHandler(console_handler)
    return the_logger
