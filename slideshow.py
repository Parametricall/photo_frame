import os
import sys
import random
import logging
import tkinter as tk
from PIL import Image, ImageTk

from utilities import (
    get_path_of_original_images,
    get_weather_from_online,
    add_text_to_image,
)
from globals import (
    SLIDESHOW_DELAY,
    GET_WEATHER_DELAY,
    IMG_DIR,
    ON_LINUX,
)

# print(IMG_DIR)

"""
# Pass slideshow delay from command line ie slideshow.py 5 If nothing passed use default 30secs
"""
try:
    SLIDESHOW_DELAY = int(sys.argv[
                              1])  # Pass slideshow delay from command line ie slideshow.py 5
except Exception as e:
    print("SLIDESHOW_DELAY incorrect")
    print(e)

try:
    IMG_DIR = sys.argv[
        2]  # Pass image directory from command line ie slideshow.py 5 '/images/'
except IndexError as e:
    print("IMG_DIR Incorrect ")
    print(e)


# if FACE_DETECTION:
#     from face_detection import static_image_face_detection


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
        random.shuffle(file_paths)
        self.pictures = iter(file_paths)

    def start_slideshow(self):
        self.get_weather()
        self.show_slides()

    def show_slides(self):
        try:
            file_path = next(self.pictures)
        except StopIteration:
            print("STOPPED iteration")
            self.fetch_slideshow_files()
            file_path = next(self.pictures)
        if file_path.endswith((".jpg", ".png")):
            self.show_image(file_path)
        else:
            logging.error(f"{file_path} is not a supported file format")
            self.show_slides()

    def show_image(self, image_path):
        original_image = Image.open(image_path)
        resized = original_image.resize(
            (self.screen_width, self.screen_height), Image.ANTIALIAS)

        add_text_to_image(resized, image_path, self.weather_icon, self.temp)

        # if FACE_DETECTION:
        #     face_image = static_image_face_detection(resized)
        #     new_img = ImageTk.PhotoImage(Image.fromarray(face_image))
        # else:
        new_img = ImageTk.PhotoImage(resized)

        self.picture_display.config(image=new_img)
        self.picture_display.image = new_img
        self.title(os.path.basename(image_path))
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
