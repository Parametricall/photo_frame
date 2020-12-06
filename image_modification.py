import os
import time
import logging
from datetime import date, datetime

from PIL import ImageDraw, ImageFont, Image

from globals import (
    GRID_SIZE,
    TEXT_COLOR,
    FONT_PATH,
    CURRENT_DATE_FORMAT,
    CURRENT_TIME_FORMAT,
    SHOW_GRID,
    CREATION_DATE_FORMAT,
    WEATHER_ICONS,
)

logger = logging.getLogger(__name__)
insane_logger = logging.getLogger("insane_logger")


class ImageModification:
    def __init__(
            self, img, image_path, weather_icon,
            temp
    ):
        logger.debug("Initializing ImageModification")
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

        self.current_date_format = CURRENT_DATE_FORMAT
        self.current_time_format = CURRENT_TIME_FORMAT
        self.creation_date_format = CREATION_DATE_FORMAT

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

        insane_logger.debug(f"image path: {self.img_path}")
        insane_logger.debug(f"image (width, height): ({self.img_width}, "
                            f"{self.img_height})")
        insane_logger.debug(f"weather icon: {self.weather_icon}")
        insane_logger.debug(f"temperature: {self.temp}")
        insane_logger.debug(
            f"grid cell (width, height): ({self.grid_cell_width}, "
            f"{self.grid_cell_height})")

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
        logger.debug("calculating base font size")
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
        logger.debug("Creating grid")
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
        logger.debug("adding current date")
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
        logger.debug("adding current time")
        current_time = time.strftime(self.current_time_format)

        font = self.get_font(int(self.base_font_size * 1.5))        
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
        logger.debug("adding img title")
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
        logger.debug("adding image creation date")
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
                logger.info(
                    f"creation date is not in expect place: {self.img_path}")
                creation_date = creation_time.split(" ")[0]
                creation_date = creation_date.split(":")
                creation_date.reverse()
                cre_date = "/".join(creation_date)
                date_obj = datetime.strptime(cre_date, "%d/%m/%Y")
            except KeyError:
                logger.warning(f"img has not creation time: {self.img_path}")
                return

            formatted_date = date_obj.strftime(self.creation_date_format)
        except BaseException as e:
            logger.warning(f"Could not get creation date for: {self.img_path}")
            logger.exception(e)
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
        logger.debug("adding img location")
        path = os.path.dirname(self.img_path)
        location = os.path.basename(path)

        split_location = location.split("_")
        clean_words = []
        for word in split_location:
            try:
                int(word)
            except ValueError:
                clean_words.append(word)

        clean_location = " ".join(clean_words)
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
        logger.debug("adding weather")
        if self.weather_icon is None:
            return

        # Add weather icon to image
        weather_icon = WEATHER_ICONS.get(self.weather_icon, None)
        minimum_icon_height = self.general_text_height * 2
        #print(f"Mininum icon height: {minimum_icon_height}")

        if minimum_icon_height < 32:
            icon_path = f"./icons/32px/{weather_icon}.png"
        elif minimum_icon_height < 64:
            icon_path = f"./icons/64px/{weather_icon}.png"
        elif minimum_icon_height < 128:
            icon_path = f"./icons/128px/{weather_icon}.png"
        elif minimum_icon_height < 220: #altered to use 192px icons, height was 216px
            icon_path = f"./icons/192px/{weather_icon}.png"
        elif minimum_icon_height < 256:
            icon_path = f"./icons/256px/{weather_icon}.png"
            print("Using 256px")
        else:
            icon_path = f"./icons/512px/{weather_icon}.png"
        icon_img = Image.open(icon_path)
        icon_width, icon_height = icon_img.size

        #x = current_date_x - self.grid_cell_width - icon_width
        x = current_date_x - int(icon_width * 1.1)
        y = self.bottom_border - icon_height

        self.img.paste(icon_img, box=(x, y), mask=icon_img)

        return x

    def add_temperature(self, weather_x):
        logger.debug("adding temperature")
        if self.temp is None or weather_x is None:
            return

        width, height = self.get_text_size(self.temp, self.base_font)

        #x = weather_x - self.grid_cell_width - width
        x = weather_x - int( width * 1.1)
        y = self.bottom_border - height

        self.draw.text(
            (x, y),
            self.temp,
            fill=TEXT_COLOR,
            font=self.base_font,
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_color,
        )
