import os
import logging
from logging_config import setup_logger

from slideshow import Slideshow
import globals

from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument(
    "slideshow_delay",
    type=int,
    help="slideshow delay in seconds",
    nargs="?",
    default=globals.SLIDESHOW_DELAY

)
parser.add_argument(
    "image_directory",
    type=str,
    help="relative or absolute path to the image directory",
    nargs="?",
    default=globals.IMG_DIR
)
parser.add_argument(
    "-l",
    "--LOG_LEVEL",
    dest="LOG_LEVEL",
    type=str,
    default=globals.LOG_LEVEL
)
parser.add_argument(
    "--INSANE_LOGGING",
    dest="INSANE_LOGGER",
    action="store_true",
    default=globals.INSANE_LOGGER
)


def main():
    if globals.ON_LINUX:
        if os.environ.get("DISPLAY", None) is None:
            os.environ["DISPLAY"] = ":0"
            logger.info("Setting environment variable: DISPLAY = :0")
        else:
            logger.debug("DISPLAY already set")

    try:
        logger.info("Initializing Slideshow")
        slideshow = Slideshow()
        slideshow.start_slideshow()
        slideshow.mainloop()
    except BaseException as e:
        logger.exception(e)


if __name__ == '__main__':
    args = parser.parse_args()
    globals.SLIDESHOW_DELAY = args.slideshow_delay
    globals.IMG_DIR = args.image_directory
    globals.LOG_LEVEL = args.LOG_LEVEL
    globals.INSANE_LOGGER = args.INSANE_LOGGER

    setup_logger()
    logger = logging.getLogger("start_slideshow")

    main()
