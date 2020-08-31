import os
import time
import random
from datetime import date, datetime
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import configparser

from utilities import *

import logging

config = configparser.ConfigParser()
config.read("./config.ini")

LOG_FILENAME = 'logging.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

# delay in seconds
SLIDESHOW_DELAY = 30

# delay in seconds
GET_WEATHER_DELAY = 1 * 3600  # 1 hours

os_name = os.name
ON_LINUX = os_name == "posix"

if ON_LINUX:
    IMG_DIR = "/media/usb/images"
else:
    IMG_DIR = "./media/usb/images"
    SLIDESHOW_DELAY = 5

TIME_FORMAT = "%H:%M"  # e.g. 18:32
DATE_FORMAT = "%a %#d %b"  # e.g Sun 16 Aug
ALT_DATE_FORMAT = "%#d %b %Y"  # 6 Nov 2018

if os.path.exists("/usr/share/fonts"):
    font_path = "/usr/share/fonts"
else:
    font_path = ""

FONT_PATH = "f{font_path}/dejavu/DejaVuSans.ttf"

# rgba
TEXT_COLOR = (255, 255, 255, 255)  # white

SHOW_GRID = False
GRID_SIZE = 20
TIME_TO_DATE_RATIO = 2

FACE_DETECTION = False
if FACE_DETECTION:
    from face_detection import static_image_face_detection


class App(tk.Tk):
    def __init__(self, paths_to_images):
        tk.Tk.__init__(self)
        self.w = self.winfo_screenwidth()
        self.h = self.winfo_screenheight()
        self.overrideredirect(1)
        self.geometry(f"{self.w}x{self.h}+0+0")
        self.delay = (SLIDESHOW_DELAY * 1000)
        self.pictures = None
        self.picture_index = None
        self.fetch_image_paths()
        self.weather = None
        self.weather_icon = None

        self.picture_display = tk.Label(self)
        self.picture_display.configure(bg="black")
        self.picture_display.pack(expand=True, fill="both")
        self.bind('<Escape>', self.close)

    def fetch_image_paths(self):
        self.pictures = get_path_of_original_images(IMG_DIR)
        random.shuffle(self.pictures)

    def get_next_random_image(self):
        num_images = len(self.pictures)
        index = self.picture_index

        if num_images == 0:
            raise RuntimeError("Could not find any images to load")

        if index is None:
            self.picture_index = 0
            return 0

        if index >= num_images - 1:
            self.fetch_image_paths()
            index = 0
        else:
            index += 1

        self.picture_index = index
        return index

    def start_slideshow(self):
        file_path = self.pictures[self.get_next_random_image()]
        if file_path.endswith((".jpg", ".png")):
            self.show_image(file_path)
        else:
            self.play_video(file_path)

    def show_slides(self):
        image_path = self.pictures[self.get_next_random_image()]
        original_image = Image.open(image_path)
        resized = original_image.resize((self.w, self.h), Image.ANTIALIAS)

        add_text_to_image(resized, image_path, self.weather_icon)

        if FACE_DETECTION:
            face_image = static_image_face_detection(resized)
            new_img = ImageTk.PhotoImage(Image.fromarray(face_image))
        else:
            new_img = ImageTk.PhotoImage(resized)

        self.picture_display.config(image=new_img)
        self.picture_display.image = new_img
        self.title(os.path.basename(image_path))
        self.after(self.delay, self.show_slides)

    # noinspection PyUnusedLocal
    def close(self, event=None):
        self.destroy()

    def get_weather(self):
        logging.info("fetching weather")
        self.weather = get_weather()
        if self.weather is None:
            logging.warning("Failed to get weather, retrying in 30 seconds")
            self.after((30 * 1000), self.get_weather)
        else:
            self.weather_icon = self.weather["icon"]
            self.after(GET_WEATHER_DELAY * 1000, self.get_weather)

if __name__ == '__main__':
    try:
        logging.info("Starting slideshow")
        image_files = get_path_of_original_images(IMG_DIR)

        app = App(image_files)
        app.get_weather()
        app.show_slides()
        app.mainloop()
    except:
        logging.exception("Got exception on main handler")
        raise
