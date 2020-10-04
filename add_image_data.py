import os
import time
from datetime import date, datetime

from PIL import ImageDraw, ImageFont, Image

from globals import (
    GRID_SIZE,
    TEXT_COLOR,
    FONT_PATH,
    DATE_FORMAT,
    TIME_FORMAT,
    SHOW_GRID,
    ALT_DATE_FORMAT,
    WEATHER_ICONS,
)


class ImageModification:
    def __init__(
            self, img, image_path, weather_icon,
            temp
    ):
        self.img = img
        self.img_path = image_path
        self.img_width, self.img_height = img.size
        self.draw = ImageDraw.Draw(img)

        self.weather_icon = weather_icon
        self.temp = temp

        self.show_grid = SHOW_GRID
        self.grid_size = GRID_SIZE
        self.grid_cell_width = int(self.img_width / self.grid_size)
        self.grid_cell_height = int(self.img_height / self.grid_size)

        self.current_date_format = DATE_FORMAT
        self.current_time_format = TIME_FORMAT
        self.creation_date_format = ALT_DATE_FORMAT

        self.general_text_height = self.grid_cell_height * 3

        self.font_path = FONT_PATH
        self.base_font, self.base_font_size = self.calculate_base_font_size()

        self.border = 1
        self.left_border = self.grid_cell_width * self.border
        self.right_border = ((self.grid_size - self.border) *
                             self.grid_cell_width)
        self.top_border = self.grid_cell_width * self.border
        self.bottom_border = ((self.grid_size - self.border) *
                              self.grid_cell_height)

        self.text_color = TEXT_COLOR
        self.stroke_color = "black"
        self.stroke_width = 3

    def add_info_to_image(self):
        if self.show_grid:
            self.add_grid()

        current_date_x = self.add_current_date()
        self.add_current_time()
        self.add_img_title()
        self.add_img_creation_date()
        self.add_img_location()
        weather_x = self.add_weather(current_date_x)
        self.add_temperature(weather_x)

    def calculate_base_font_size(self):
        sample_text = "Hello World 0158"
        font_size = 1
        font = self.get_font(font_size=font_size)
        _, sample_height = self.get_text_size(sample_text, font)

        while sample_height < self.general_text_height:
            font_size += 1
            font = self.get_font(font_size=font_size)
            _, sample_height = self.get_text_size(sample_text, font)

        return font, font_size

    def get_text_size(self, ink, font):
        return self.draw.textsize(ink, font)

    def get_font(self, font_size):
        return ImageFont.truetype(self.font_path, font_size)

    def add_grid(self):
        for i in range(1, self.grid_size + 1):
            self.draw.line(
                [
                    (i * self.grid_cell_width, 0),
                    (i * self.grid_cell_width, self.img_height),
                ],
                fill="purple",
                width=5,
            )
            self.draw.line(
                [
                    (0, i * self.grid_cell_height),
                    (self.img_width, i * self.grid_cell_height),
                ],
                fill="purple",
                width=5,
            )

    def add_current_date(self):
        current_date = date.today().strftime(self.current_date_format)
        width, height = self.get_text_size(current_date, self.base_font)
        x = self.right_border - width
        y = self.bottom_border - height

        self.draw.text(
            (x, y),
            current_date,
            fill=self.text_color,
            font=self.base_font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )

        return x

    def add_current_time(self):
        current_time = time.strftime(self.current_time_format)

        font = self.get_font(self.base_font_size * 2)
        width, height = self.get_text_size(current_time, font)
        x = self.right_border - width
        y = self.bottom_border - self.general_text_height - height
        self.draw.text(
            (x, y),
            current_time,
            fill=self.text_color,
            font=font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )

    def add_img_title(self):
        exif = self.img.getexif()
        img_title = (exif.get(270, "").strip())

        font = self.get_font(int(self.base_font_size * 1.5))
        width, height = self.get_text_size(img_title, font)

        x = self.img_width / 2 - width / 2
        y = self.bottom_border - height

        self.draw.text(
            (x, y),
            img_title,
            fill=self.text_color,
            font=font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )

    def add_img_creation_date(self):
        exif = self.img.getexif()
        creation_time = exif.get(36867)

        # noinspection PyBroadException
        try:
            if creation_time is None:
                creation_time = self.img.info["Creation Time"]
            try:
                date_obj = datetime.strptime(
                    creation_time,
                    "%a %d %b %Y %H:%M:%S %z"
                )
            except ValueError:
                creation_date = creation_time.split(" ")[0]
                creation_date = creation_date.split(":")
                creation_date.reverse()
                cre_date = "/".join(creation_date)
                date_obj = datetime.strptime(cre_date, "%d/%m/%Y")

            formatted_date = date_obj.strftime(self.creation_date_format)
        except BaseException:
            return

        x = self.left_border
        y = self.bottom_border - self.general_text_height

        self.draw.text(
            (x, y),
            formatted_date,
            fill=self.text_color,
            font=self.base_font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )

    def add_img_location(self):
        if self.img_path is None:
            return

        path = os.path.dirname(self.img_path)
        location = os.path.basename(path)
        clean_location = " ".join(location.split("_"))
        _, height = self.get_text_size(clean_location, self.base_font)
        x = self.left_border
        y = self.bottom_border - self.general_text_height - height

        self.draw.text(
            (x, y),
            clean_location,
            fill=self.text_color,
            font=self.base_font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )

    def add_weather(self, current_date_x):
        if self.weather_icon is None:
            return

        # Add weather icon to image
        weather_icon = WEATHER_ICONS.get(self.weather_icon, None)
        if self.grid_cell_width < 35:
            icon_path = f"./icons/128px/{weather_icon}.png"
        else:
            icon_path = f"./icons/128px/{weather_icon}.png"
        icon_img = Image.open(icon_path)
        icon_width, icon_height = icon_img.size

        x = current_date_x - (self.grid_cell_width * 2) - icon_width
        y = self.bottom_border - icon_height

        self.img.paste(icon_img, box=(x, y), mask=icon_img)

        return x

    def add_temperature(self, weather_x):
        if self.temp is None:
            return

        width, height = self.get_text_size(self.temp, self.base_font)

        x = weather_x - self.grid_cell_width - width
        y = self.bottom_border - height

        self.draw.text(
            (x, y),
            self.temp,
            fill=TEXT_COLOR,
            font=self.base_font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )