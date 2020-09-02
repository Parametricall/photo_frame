"""
Montage creator

IDEAS:

Im thinking a script you run, it search through the images directory,
collects all images, analyzes size of the image, randomly generates
a montage from the images and displays the new montage img to the user.

Using tkinter, if the user approves of the montage, have button to click
save, and another button to click discard.  Loop over all the images,
with different montage creations. Refine the script in the future to
maybe bias towards a specific structure or add more variations.

have the script pre-load the next few images to speed up transition to
next image.

tkinter shuffle button to shuffle current montage

"""

import random
import tkinter as tk
from PIL import Image, ImageTk

from utilities import get_path_of_original_images

IMG_DIR = "./media/usb/images/Disneyland_2005"
MONTAGE_DIR = "./media/usb/images/montages"


def create_montage(width, height, image_paths, margin=10):
    grid_size = 2

    cell_width = width // grid_size
    cell_height = height // grid_size
    new_im = Image.new('RGB', (width, height))

    cell_images = []
    for img_path in image_paths:
        img = Image.open(img_path)
        img_w, img_h = img.size
        resize = img.resize((img_w // grid_size, img_h // grid_size),
                            Image.ANTIALIAS)
        cropped = resize.crop((margin, margin, img_w - margin, img_h - margin))
        cell_images.append(cropped)

    i = 0
    x = 0
    y = 0
    for col in range(grid_size):
        for row in range(grid_size):
            if x + cell_width == width:
                x += margin

            if y + cell_height == height:
                y += margin

            try:
                new_im.paste(cell_images[i], (x, y))
            except IndexError:
                continue
            i += 1
            y += cell_height
        x += cell_width
        y = 0

    return new_im


class Montage(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.config(bg="skyblue")
        self.bind('<Escape>', self.close)

        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side="left", expand=True)

        tk.Label(self.left_frame, text="Example Text").pack(side="top")
        self.create_button = tk.Button(
            self.left_frame,
            text="Create Montage",
            command=self.create_montage
        )
        self.create_button.pack(side="bottom")

        self.save_montage = tk.Button(
            self.left_frame,
            text="Save Montage",
            command=self.save_montage,
        )
        self.save_montage.pack(side="bottom")

        self.montage = tk.Label(self)
        self.montage.pack(side="right", expand=True)
        self.new_montage = None

    def create_montage(self):
        image_paths = get_path_of_original_images(IMG_DIR)
        random.shuffle(image_paths)
        new_montage = create_montage(3840, 2160, image_paths)
        self.show_montage(new_montage)
        self.new_montage = new_montage

    def show_montage(self, image):
        new_width = int(self.screen_width * 0.8)
        new_height = int(self.screen_height * 0.8)

        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        ph = ImageTk.PhotoImage(image)

        self.montage.config(image=ph, bg="skyblue")
        self.montage.image = ph
        self.montage.pack(expand=True, side="right")

    def save_montage(self):
        path = f"{MONTAGE_DIR}/new_montage.jpg"
        self.new_montage.save(path)

    # noinspection PyUnusedLocal
    def close(self, event=None):
        self.destroy()


if __name__ == '__main__':
    montage = Montage()
    montage.mainloop()
