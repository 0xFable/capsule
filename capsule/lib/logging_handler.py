"""Once Place for logging stuff"""
import logging


def setup_logger(logger_name="capsule", extra_kwargs={}):
    """Simple wrapper to setup a logger and return it.
    Used by the LOG constant which is used through the project

    Args:
        logger_name (str, optional): The name for the logger. Defaults to "capsule".
        extra_kwargs (dict, optional): Any extra options to use with the logger. Defaults to {}.
    """
    logger = logging.getLogger(logger_name, **extra_kwargs)
    logger.setLevel(logging.INFO)
    # Setup a StreamHandler to give output to the logs
    handler = logging.StreamHandler()
    # Establish a log format for messages
    handler.setFormatter(logging.Formatter('[capsule:%(module)s] %(message)s'))
    # Add handler to logger
    logger.addHandler(handler)
    return logger

LOG = setup_logger()
