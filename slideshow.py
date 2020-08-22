import os
import time
import random
import json
import requests
from datetime import date, datetime
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

import logging
LOG_FILENAME = 'logging.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)


logging.info("test debug")

# delay in seconds
SLIDESHOW_DELAY = 300

os_name = os.name
ON_LINUX = os_name == "posix"

if ON_LINUX:
    IMG_DIR = "/media/usb/images"
else:
    IMG_DIR = "./media/usb/images/Disneyland_2005"

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


BRISBANE_LAT = 27.4698
BRISBANE_LON = 153.0251

EXCLUDE = "minutely,hourly"

API_TOKEN = "d1414e08ebfc105903662cc153faf764"
API_URL = f"https://api.openweathermap.org/data/2.5/onecall?lat" \
          f"={BRISBANE_LAT}" \
               f"&lon={BRISBANE_LON}&exclude={EXCLUDE}&appid={API_TOKEN}"


def get_weather():
    response = requests.get(API_URL)

    if response.status_code == 200:
        json_res = json.loads(response.content)
        weather = json_res["current"]["weather"][0]
        icon = weather["icon"]
        # icon_response = requests.get("http://openweathermap.org/img/w/" +
        #                            weather[
        #     'icon'] +
        # ".png")
        # print("success")
        #
        # # icon = icon_response.raw.decode
        # file = open("./icons/test.png", "wb")
        # file.write(icon_response.content)
        # file.close()
        # with open(IMG_DIR, 'w') as f:
        #     f.write(img)

        return weather["main"], icon
    else:
        raise RuntimeError("request for weather failed")


class App(tk.Tk):
    def __init__(self, paths_to_images):
        tk.Tk.__init__(self)
        self.w = self.winfo_screenwidth()
        self.h = self.winfo_screenheight()
        self.overrideredirect(1)
        self.geometry(f"{self.w}x{self.h}+0+0")
        self.delay = (SLIDESHOW_DELAY * 1000)
        self.pictures = paths_to_images

        self.weather, self.icon = get_weather()

        self.picture_display = tk.Label(self)
        self.picture_display.pack(expand=True, fill="both")
        self.bind('<Escape>', self.close)

    def show_slides(self):
        image_path = random.choice(self.pictures)
        original_image = Image.open(image_path)
        resized = original_image.resize((self.w, self.h), Image.ANTIALIAS)

        add_text_to_image(resized, image_path, self.icon)

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


def add_text_to_image(img, image_path, icon):
    img_width, img_height = img.size
    cell_width = int(img_width / GRID_SIZE)
    cell_height = int(img_height / GRID_SIZE)

    draw = ImageDraw.Draw(img)

    if SHOW_GRID:
        show_grid(draw, cell_width, cell_height, img_width,
                  img_height)

    date_font_size = add_current_time_to_image(draw, cell_width, cell_height,)
    add_location_and_year(draw, img, image_path,
                          cell_width, cell_height,
                          date_font_size)

    icon_path = f"./icons/64_bit/{icon}.png"
    icon_img = Image.open(icon_path)
    icon_width, icon_height = icon_img.size

    x = ((GRID_SIZE - 4) * cell_width) - (icon_width//2)
    y = (GRID_SIZE - 3) * cell_height - 10
    img.paste(icon_img, box=(x, y), mask=icon_img)


def add_location_and_year(
        draw,
        img,
        path,
        cell_width,
        cell_height,
        date_font_size,
):
    exif = img.getexif()

    creation_time = exif.get(36867)
    creation_date = creation_time.split(' ')[0]
    creation_date = creation_date.split(':')
    creation_date.reverse()
    cre_date = '/'.join(creation_date)

    date_obj = datetime.strptime(cre_date, "%d/%m/%Y")

    formatted_date = date_obj.strftime(ALT_DATE_FORMAT)

    rel_folders, _ = os.path.split(path)
    folders = rel_folders.split("/")
    cur_folder = folders[-1]
    dir_name = " ".join(cur_folder.split('_')[:-1])
    dir_name = dir_name.replace("\\", "")

    meta_font, meta_width, meta_height = get_font_width_height(
        draw, creation_time, date_font_size
    )

    x_pos = cell_width
    y_pos = int((GRID_SIZE - 2) * cell_height)
    draw.text((x_pos, y_pos), formatted_date, fill=TEXT_COLOR,
              font=meta_font, stroke_width=3, stroke_fill="black")

    draw.text((x_pos, int((GRID_SIZE - 3) * cell_height)), dir_name,
              fill=TEXT_COLOR,
              font=meta_font, stroke_width=3, stroke_fill="black")


def add_current_time_to_image(
        draw,
        cell_width,
        cell_height,
):
    display_time = time.strftime(TIME_FORMAT)
    display_date = date.today().strftime(DATE_FORMAT)

    font_info = get_font_info(draw, display_date, display_time, cell_height)

    time_font = font_info["time"]
    date_font = font_info["date"]
    date_font_size = font_info["date_font_size"]

    # Align time with end of date string
    width_offset = date_font["width"] - time_font["width"]
    offset = ((GRID_SIZE - 1) * cell_width) - date_font["width"]
    date_coord_x = offset
    date_coord_y = int((GRID_SIZE - 2) * cell_height)

    time_coord_x = date_coord_x + width_offset
    time_coord_y = date_coord_y - time_font["height"] - 2

    print(f"date font = {date_font_size}")

    draw.text((time_coord_x, time_coord_y), display_time, fill=TEXT_COLOR,
              font=time_font["font"], stroke_width=3, stroke_fill="black")
    draw.text((date_coord_x, date_coord_y), display_date, fill=TEXT_COLOR,
              font=date_font["font"], stroke_width=3, stroke_fill="black")

    return date_font_size


def show_grid(draw, cell_width, cell_height, img_width, img_height):
    for i in range(1, GRID_SIZE + 1):
        draw.line([(i * cell_width, 0), (i * cell_width + 10, img_height)],
                  fill="purple",
                  width=5)
        draw.line([(0, i * cell_height), (img_width, i * cell_height + 10)],
                  fill="purple",
                  width=5)


def get_font_width_height(draw, ink, font_size, ratio=1):
    try:
        font = ImageFont.truetype(FONT_PATH, int(
            font_size * ratio))
    except OSError:
        font = ImageFont.truetype("arial.ttf", int(
            font_size * ratio))

    width, height = draw.textsize(ink, font)

    return font, width, height


def get_font_info(draw, display_date, display_time, cell_height):
    date_font_size = 1

    date_font, date_width, date_height = get_font_width_height(
        draw, display_date, date_font_size
    )
    time_font, time_width, time_height = get_font_width_height(
        draw, display_time, date_font_size, ratio=TIME_TO_DATE_RATIO
    )

    while date_height < cell_height:
        time_font, time_width, time_height = get_font_width_height(
            draw, display_time, date_font_size, ratio=TIME_TO_DATE_RATIO
        )
        date_font, date_width, date_height = get_font_width_height(
            draw, display_date, date_font_size
        )
        date_font_size += 1

    return {
        "time": {
            "font": time_font,
            "width": time_width,
            "height": time_height,
        },
        "date": {
            "font": date_font,
            "width": date_width,
            "height": date_height,
        },
        "date_font_size": date_font_size,
    }


def get_path_of_original_images(img_dir=IMG_DIR):
    files = os.scandir(img_dir)

    images = []
    for file in files:
        if file.is_dir():
            images += get_path_of_original_images(file.path)
            continue
        if file.name.endswith(".jpg"):
            images.append(f"{img_dir}/{file.name}")

    return images


if __name__ == '__main__':
    try:
        image_files = get_path_of_original_images()

        app = App(image_files)
        app.show_slides()
        app.mainloop()
    except:
        logging.exception("Got exception on main handler")
        raise
