Photo Frame
===========

Simple image modification script to add current time and date to the bottom right of an image,
and also add the location and date the photo was taken to the bottom left.

This project was created to run on a raspberry pi 4 connected to a 4k TV which is being
used as an electronic photo frame.  Currently we are using the linux module "feh" to view
the images as a slideshow.

The image modification script fins the path to all images in the IMG_DIR location and
randomly loads an image, applys the time, date, and location, then outputs to a 
"display_photo/output.jpg" file.  "feh" then reads in this file and displays it, and 
reloads the image every x seconds.  Within the x seconds, python has loaded a new image 
so the image on the TV changes every x seconds.