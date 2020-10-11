#!/bin/bash

cd /home/pi/PySpace/photo_frame/

echo "Time: $(date) ready" >> startup.log

poetry run python start_slideshow.py

# examples
#poetry run python slideshow.py slideshow_delay image_directory --LOG_LEVEL LOGLEVEL --INSANE_LOGGING
#poetry run python slideshow.py 30 /media/usb/images --LOG_LEVEL INFO --INSANE_LOGGING
#poetry run python slideshow.py --INSANE_LOGGING

