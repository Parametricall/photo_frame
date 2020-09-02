#!/bin/bash

cd /home/pi/PySpace/photo_frame/

echo "Time: $(date) ready" >> startup.log

poetry run python slideshow.py

