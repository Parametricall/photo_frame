import logging.config

import globals


def setup_logger():
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
                "filename": "logging.out",
                "formatter": "verbose",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
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
