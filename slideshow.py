import os
import sys
import requests
import json
import random
import logging

import tkinter as tk
from PIL import Image, ImageTk
from requests.adapters import HTTPAdapter

from image_modification import ImageModification
from globals import (
    SLIDESHOW_DELAY,
    GET_WEATHER_DELAY,
    IMG_DIR,
    ON_LINUX, API_URL_BASE, API_URL, EXCLUDE_DIRS,
)


def get_weather_from_online():
    try:
        session = requests.Session()
        session.mount(API_URL_BASE, HTTPAdapter(
            max_retries=3))
        response = session.get(API_URL)
    except requests.exceptions.ConnectionError as error:
        logging.error(error)
        return None, None

    if response.status_code == 200:
        json_res = json.loads(response.content)
        weather = json_res["hourly"][1]["weather"][0]
        temp = json_res["hourly"][0]["temp"] - 273
        temp = "{:2.0f}".format(temp)
        temp = temp + u"\N{DEGREE SIGN}"
    else:
        weather = None
        temp = None

    return weather, temp


def get_path_of_original_images(img_dir=IMG_DIR):
    files = os.scandir(img_dir)
    images = []
    for file in files:
        if file.is_dir():
            if file.name in EXCLUDE_DIRS:
                pass
            else:
                output = get_path_of_original_images(file.path)
                images += output
            continue
        if file.name.endswith((".jpg", ".png", ".MP4")):
            images.append(f"{img_dir}/{file.name}")

    return images


class Slideshow(tk.Tk):
    def __init__(self):
        # Setup main window
        super().__init__()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.overrideredirect(True)
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.bind('<Escape>', self.close)

        # Setup Label widget (for displaying images)
        self.picture_display = tk.Label(self)
        self.picture_display.configure(bg="black")
        self.picture_display.pack(expand=True, fill="both")

        # Extras
        self.pictures = None
        self.picture_index = 0
        self.number_of_images = None
        self.fetch_slideshow_files()

        self.weather = None
        self.weather_icon = None
        self.temp = None

        self.delay = (SLIDESHOW_DELAY * 1000)

    def get_weather(self):
        """
        This method is set to run every "GET_WEATHER_DELAY" seconds.  It
        will run in the background and should not affect the image
        slideshow.  If the weather cannot be fetched, then it will retry
        after 30 seconds.
        """
        logging.info("fetching weather")
        self.weather, self.temp = get_weather_from_online()
        if self.weather is None:
            logging.warning("Failed to get weather, retrying in 30 seconds")
            self.after((30 * 1000), self.get_weather)
        else:
            self.weather_icon = self.weather["icon"]
            self.after(GET_WEATHER_DELAY * 1000, self.get_weather)
        if self.temp is None:
            self.temp = ""

    def fetch_slideshow_files(self):
        logging.info("Building file list")
        image_paths = get_path_of_original_images(IMG_DIR)
        self.number_of_images = len(image_paths)
        logging.info(f"Found: {len(image_paths)} images")
        random.shuffle(image_paths)
        self.pictures = image_paths

    def start_slideshow(self):
        self.get_weather()
        self.show_slides()

    def show_slides(self):
        if self.number_of_images is not None:
            if self.picture_index < self.number_of_images:
                logging.info(f"fetching image {self.picture_index + 1}")
                image_path = self.pictures[self.picture_index]
                self.picture_index += 1
            else:
                logging.info("End of image path array")
                self.fetch_slideshow_files()
                logging.info(f"fetching image 0")
                image_path = self.pictures[0]
                self.picture_index = 1
        else:
            raise NotImplementedError("number of images is still None")

        self.show_image(image_path)

    def show_image(self, image_path):
        original_image = Image.open(image_path)
        resized = original_image.resize(
            (self.screen_width, self.screen_height), Image.ANTIALIAS)

        modified_img = ImageModification(resized, image_path,
                                         self.weather_icon, self.temp)
        modified_img.add_info_to_image()

        new_img = ImageTk.PhotoImage(resized)

        self.picture_display.config(image=new_img)
        self.picture_display.image = new_img
        self.after(self.delay, self.show_slides)

    # noinspection PyUnusedLocal
    def close(self, event=None):
        self.destroy()


if __name__ == '__main__':
    LOG_FILENAME = 'logging.out'
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Pass slideshow delay from command line i.e. slideshow.py 5
    # If nothing passed use default 30 secs
    try:
        SLIDESHOW_DELAY = int(sys.argv[1])
    except IndexError:
        logging.info(f"Using default delay {SLIDESHOW_DELAY}")

    # Pass image directory from command line
    # i.e. slideshow.py 5 /media/usb/images
    try:
        IMG_DIR = sys.argv[2]
    except IndexError:
        logging.info(f"Using default image directory {IMG_DIR} ")

    if ON_LINUX:
        if os.environ.get("DISPLAY", None) is None:
            os.environ["DISPLAY"] = ":0"
            logging.info("Setting environment variable: DISPLAY = :0")

    try:
        logging.info("Initializing Slideshow")
        slideshow = Slideshow()
        logging.info("Starting slideshow")
        slideshow.start_slideshow()
        slideshow.mainloop()
    except BaseException as e:
        logging.exception(e)
        raise
