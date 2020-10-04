import json
import os
import random
import logging
import sys
import tkinter as tk

import requests
from PIL import Image, ImageTk
from requests.adapters import HTTPAdapter

from image_modification import ImageModification
from globals import (
    SLIDESHOW_DELAY,
    GET_WEATHER_DELAY,
    IMG_DIR,
    ON_LINUX, API_URL_BASE, API_URL, EXCLUDE_DIRS,
)
from montage_generator import create_montage

try:
    # Pass slideshow delay from command line i.e. slideshow.py 5
    # If nothing passed use default 30 secs
    SLIDESHOW_DELAY = int(sys.argv[1])
except Exception as e:
    print("SLIDESHOW_DELAY incorrect")
    print(e)
    # logging.warning(e)

try:
    # Pass image directory from command line
    # i.e. slideshow.py 5 /media/usb/images
    IMG_DIR = sys.argv[2]
except IndexError as e:
    print("IMG_DIR Incorrect ")
    print(e)
    # logging.warning(e)


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

    images_to_montage = []
    images = []
    for file in files:
        if file.is_dir():
            if file.name in EXCLUDE_DIRS:
                pass
            elif file.name == "montage":
                output = get_path_of_original_images(file.path)
                images_to_montage += [output["images"]]
            else:
                output = get_path_of_original_images(file.path)
                images += output["images"]
                images_to_montage += output["montage"]
            continue
        if file.name.endswith((".jpg", ".png", ".MP4")):
            images.append(f"{img_dir}/{file.name}")

    return {"images": images, "montage": images_to_montage}


class Slideshow(tk.Tk):
    def __init__(self):
        # Setup main window
        tk.Tk.__init__(self)
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
        self.picture_index = None
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
        file_paths = get_path_of_original_images(IMG_DIR)

        single_images = file_paths["images"]
        images = [(Image.open(img_path), img_path) for img_path in
                  single_images]

        for montage in file_paths["montage"]:
            num_photos = len(montage)
            num_photos_in_montage = 4

            num_montages = num_photos // num_photos_in_montage
            extra_montage = num_photos % num_photos_in_montage

            montage_images = []
            for i in range(num_montages):
                new_montage = create_montage(
                    3840, 2160,
                    montage[(i * num_photos_in_montage):num_photos_in_montage]
                )
                montage_images.append((new_montage, ""))

            if extra_montage:
                extra = create_montage(
                    3840, 2160, montage[(-1 * num_photos_in_montage):])
                montage_images.append((extra, ""))

            images += montage_images
        random.shuffle(images)

        self.pictures = iter(images)

    def start_slideshow(self):
        self.get_weather()
        self.show_slides()

    def show_slides(self):
        try:
            image = next(self.pictures)
        except StopIteration:
            print("STOPPED iteration")
            self.fetch_slideshow_files()
            image = next(self.pictures)

        self.show_image(image)

    def show_image(self, image):
        original_image = image[0]
        image_path = image[1]
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

    if ON_LINUX:
        if os.environ.get("DISPLAY", None) is None:
            os.environ["DISPLAY"] = ":0"
            logging.info("Setting environment variable: DISPLAY = :0")

    try:
        logging.info("Starting slideshow")
        slideshow = Slideshow()
        slideshow.start_slideshow()
        slideshow.mainloop()
    except BaseException as e:
        logging.exception(e)
        raise
