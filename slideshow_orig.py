import os
import random
import logging
import tkinter as tk
from PIL import Image, ImageTk

from utilities_orig import (
    get_path_of_original_images,
    get_weather_from_online,
    add_text_to_image,
)
from globals import (
    SLIDESHOW_DELAY,
    GET_WEATHER_DELAY,
    IMG_DIR,
    FACE_DETECTION, ON_LINUX,
)
from montage_generator import create_montage

if FACE_DETECTION:
    from face_detection import static_image_face_detection


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

        self.delay = (SLIDESHOW_DELAY * 1000)

    def get_weather(self):
        """
        This method is set to run every "GET_WEATHER_DELAY" seconds.  It
        will run in the background and should not affect the image
        slideshow.  If the weather cannot be fetched, then it will retry
        after 30 seconds.
        """
        logging.info("fetching weather")
        self.weather = get_weather_from_online()
        if self.weather is None:
            logging.warning("Failed to get weather, retrying in 30 seconds")
            self.after((30 * 1000), self.get_weather)
        else:
            self.weather_icon = self.weather["icon"]
            self.after(GET_WEATHER_DELAY * 1000, self.get_weather)

    def fetch_slideshow_files(self):
        file_paths = get_path_of_original_images(IMG_DIR)

        single_images = file_paths["images"]
        images = [Image.open(img) for img in single_images]

        for montage in file_paths["montage"]:
            random.shuffle(montage)
            num_photos = len(montage)
            num_photos_in_montage = 4

            num_montages = num_photos // num_photos_in_montage
            extra_montage = num_photos % num_photos_in_montage

            montage_images = []
            for i in range(num_montages):
                new_montage = create_montage(3840, 2160, montage[(i *
                                                                  num_photos_in_montage):num_photos_in_montage])
                montage_images.append(new_montage)

            if extra_montage:
                montage_images.append(create_montage(3840, 2160, montage[(-1 *
                                                                          num_photos_in_montage):]))

            images += montage_images
        random.shuffle(images)

        self.pictures = iter(images)

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

        self.show_image(file_path)

    def show_image(self, image_path):
        # original_image = Image.open(image_path)
        original_image = image_path
        resized = original_image.resize(
            (self.screen_width, self.screen_height), Image.ANTIALIAS)

        add_text_to_image(resized, image_path, self.weather_icon)

        if FACE_DETECTION:
            face_image = static_image_face_detection(resized)
            new_img = ImageTk.PhotoImage(Image.fromarray(face_image))
        else:
            new_img = ImageTk.PhotoImage(resized)

        self.picture_display.config(image=new_img)
        self.picture_display.image = new_img
        # self.title(os.path.basename(image_path))
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
