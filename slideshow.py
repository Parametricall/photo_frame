import os
import requests
import json
import random
import logging
import vlc
import tkinter as tk
from PIL import Image, ImageTk
from requests.adapters import HTTPAdapter

from image_modification import ImageModification
from globals import (
    GET_WEATHER_DELAY,
    API_URL_BASE, API_URL, EXCLUDE_DIRS, ON_LINUX
)
import globals

logger = logging.getLogger(__name__)


def get_weather_from_online():
    try:
        session = requests.Session()
        session.mount(API_URL_BASE, HTTPAdapter(
            max_retries=3))
        response = session.get(API_URL)

        if response.status_code == 200:
            json_res = json.loads(response.content)
            weather = json_res["hourly"][1]["weather"][0]
            temp = json_res["hourly"][0]["temp"] - 273
            temp = "{:2.0f}".format(temp)
            temp = temp + u"\N{DEGREE SIGN}"
        else:
            logger.warning(f"Weather API response did not return 200 "
                           f"instead: {response.status_code}")
            weather, temp = None, None
    except requests.exceptions.ConnectionError as error:
        logger.error(error)
        weather, temp = None, None

    return weather, temp


def get_path_of_original_images(img_dir=globals.IMG_DIR):
    files = os.scandir(img_dir)
    images = []
    for file in files:
        if file.is_dir():
            if file.name in EXCLUDE_DIRS:
                pass
            else:
                output = get_path_of_original_images(file.path)
                images += output
        elif file.name.endswith((".jpg", ".png", ".mp4", ".MP4")):
            images.append(f"{img_dir}/{file.name}")
        else:
            logger.warning(f"Not supported file format: {file.path}")

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

        # Setup Frame widget (to hold vlc player instance)
        self.video_panel = tk.Frame(self)

        # Initialise vlc player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

        # Extras
        self.pictures = None
        self.picture_index = 0
        self.number_of_images = None
        self.fetch_slideshow_files()

        self.weather = None
        self.weather_icon = None
        self.temp = None

        self.delay = (globals.SLIDESHOW_DELAY * 1000)

    def get_weather(self):
        """
        This method is set to run every "GET_WEATHER_DELAY" seconds.  It
        will run in the background and should not affect the image
        slideshow.  If the weather cannot be fetched, then it will retry
        after 30 seconds.
        """
        logger.info("fetching weather")
        self.weather, self.temp = get_weather_from_online()
        if self.weather is None:
            logger.warning("Failed to get weather, retrying in 30 seconds")
            self.after((30 * 1000), self.get_weather)
        else:
            self.weather_icon = self.weather["icon"]
            self.after(GET_WEATHER_DELAY * 1000, self.get_weather)
        if self.temp is None:
            self.temp = ""

    def fetch_slideshow_files(self):
        logger.info("Building file list")
        image_paths = get_path_of_original_images(globals.IMG_DIR)
        self.number_of_images = len(image_paths)
        logger.info(f"Found: {self.number_of_images} images")
        random.shuffle(image_paths)
        self.pictures = image_paths

    def start_slideshow(self):
        logger.info("Starting Slideshow")
        self.get_weather()
        self.show_slides()

    def show_slides(self):
        if self.number_of_images is not None:
            if self.picture_index < self.number_of_images:
                image_path = self.pictures[self.picture_index]
                logger.info(
                    f"fetching image {self.picture_index + 1}: {image_path}"
                )
                self.picture_index += 1
            else:
                logger.info("End of image path array")
                self.fetch_slideshow_files()
                image_path = self.pictures[0]
                logger.info(f"fetching image 1: {image_path}")
                self.picture_index = 1
        else:
            raise NotImplementedError("number of images is still None")

        # self.show_image(image_path)
        if image_path.endswith((".jpg", ".png")):
            self.show_image(image_path)
        elif image_path.endswith((".MP4", ".mp4")):
            self.play_video(image_path)
        else:
            raise NotImplementedError("We shouldn never reach here")

    def show_image(self, image_path):
        self.video_panel.pack_forget()
        self.picture_display.pack(expand=True, fill="both")

        logger.debug("Opening image")
        original_image = Image.open(image_path)
        resized = original_image.resize(
            (self.screen_width, self.screen_height), Image.ANTIALIAS)

        logger.debug("Getting ready to modify image with data")
        modified_img = ImageModification(resized, image_path,
                                         self.weather_icon, self.temp)
        modified_img.add_info_to_image()

        new_img = ImageTk.PhotoImage(resized)

        logger.debug("Pushing image to display")
        self.picture_display.config(image=new_img)
        self.picture_display.image = new_img
        self.after(self.delay, self.show_slides)

    def play_video(self, video_path):
        self.picture_display.pack_forget()
        self.video_panel.pack(fill=tk.BOTH, expand=True)
        self.vlc_player.stop()

        logger.info("Setting up video")

        #if ON_LINUX:
            #self.vlc_player.set_xwindow(self.video_panel.winfo_id())
        #else:
            #self.vlc_player.set_hwnd(self.video_panel.winfo_id())

        media = self.vlc_instance.media_new(video_path)  # media instance
        self.vlc_player.set_media(media)  # set media used by media player
        # self.player.set_fullscreen(True)

        logger.debug("Starting video")
        #self.vlc_player.play()
        os.system(f'cvlc -f {video_path}')
        while not self.vlc_player.is_playing():
            pass

        self.title(os.path.basename(video_path))
        self.after(self.vlc_player.get_length(), self.show_slides)

    # noinspection PyUnusedLocal
    def close(self, event=None):
        self.destroy()
