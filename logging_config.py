import logging.config
import os
import globals
import time


def setup_logger():
    log_path = os.path.join(os.getcwd(), "temp")

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_name = f"log_{time.strftime('%Y-%m-%d_%H%M')}.txt"
    log_file_path = os.path.join(log_path, log_file_name)

    logging_dict = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": ("%(process)d:"
                           " %(asctime)s"
                           " %(levelname)s:"
                           "%(name)s("
                           "%(lineno)d):"
                           "%(message)s"
                           )
            },
            "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
        },
        "handlers": {
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": log_file_path,
                "formatter": "verbose",
                "mode": "w",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "null": {
                "class": "logging.NullHandler",
                "level": "DEBUG",
            }
        },
        "loggers": {
            "start_slideshow": {
                "handlers": ["console"],
                "level": globals.LOG_LEVEL,
            },
            "slideshow": {
                "handlers": ["console"],
                "level": globals.LOG_LEVEL,
            },
            "image_modification": {
                "handlers": ["console"],
                "level": globals.LOG_LEVEL
            },
        },
        "root": {"handlers": ["file"], "level": "WARNING"},
    }

    if globals.INSANE_LOGGER:
        logging_dict["loggers"]["insane_logger"] = {
            "handlers": ["console"],
            "level": "DEBUG"
        }

    logging.config.dictConfig(logging_dict)
