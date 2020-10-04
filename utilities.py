import os
import time
import json
import requests
import logging
from requests.adapters import HTTPAdapter
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
from globals import API_URL_BASE, API_URL, GRID_SIZE, TEXT_COLOR, SHOW_GRID, \
    TIME_FORMAT, ALT_DATE_FORMAT, TIME_TO_DATE_RATIO, FONT_PATH, \
    DATE_FORMAT, IMG_DIR, EXCLUDE_DIRS, WEATHER_ICONS


# def get_weather_from_online():
#     try:
#         session = requests.Session()
#         session.mount(API_URL_BASE, HTTPAdapter(
#             max_retries=3))
#         response = session.get(API_URL)
#     except requests.exceptions.ConnectionError as e:
#         logging.error(e)
#         return None, None
#
#     if response.status_code == 200:
#         json_res = json.loads(response.content)
#         weather = json_res["hourly"][1]["weather"][0]
#         temp = json_res["hourly"][0]["temp"] - 273
#         temp = "{:2.0f}".format(temp)
#         temp = temp + u"\N{DEGREE SIGN}"
#     else:
#         weather = None
#         temp = None
#
#     return weather, temp


def add_text_to_image(img, image_path, icon, temp, grid_size=GRID_SIZE,
                      show_grid=SHOW_GRID):
    img_width, img_height = img.size
    cell_width = int(img_width / grid_size)
    cell_height = int(img_height / grid_size)

    draw = ImageDraw.Draw(img)

    if show_grid:
        draw_grid(draw, cell_width, cell_height, img_width,
                  img_height)

    date_font_size, date_coord_x = add_current_time_to_image(draw, cell_width,
                                                             cell_height, )
    add_location_and_year(draw, img, image_path,
                          cell_width, cell_height,
                          date_font_size)

    # Add weather icon to image
    weather_icon = WEATHER_ICONS.get(icon, None)
    if weather_icon is not None:
        if cell_width < 35:
            icon_path = f"./icons/128px/{weather_icon}.png"
        else:
            icon_path = f"./icons/128px/{weather_icon}.png"
        icon_img = Image.open(icon_path)
        icon_width, icon_height = icon_img.size

        # x = int(((grid_size - 4) * cell_width) - icon_width)
        x = int(date_coord_x - cell_width - icon_width)
        # y = int((grid_size - 3) * cell_height + (icon_height / 3))
        y = int(((grid_size - 1) * cell_height) - icon_height)

        img.paste(icon_img, box=(x, y), mask=icon_img)

        meta_font, meta_width, meta_height = get_font_width_height(
            draw, temp, date_font_size)

        # temp_x = int(((grid_size - 4) * cell_width) - (2.5 * icon_width))
        temp_x = (x - cell_width - meta_width)
        # temp_y = int(((grid_size - 3) * cell_height)  + (icon_height / 2.5))
        temp_y = int((grid_size - 4) * cell_height)

        draw.text((temp_x, temp_y), temp, fill=TEXT_COLOR,
                  font=meta_font, stroke_width=3, stroke_fill="black")


def add_location_and_year(
        draw,
        img,
        path,
        cell_width,
        cell_height,
        date_font_size,
        alt_date_format=ALT_DATE_FORMAT,
        grid_size=GRID_SIZE,
        text_color=TEXT_COLOR,
):
    exif = img.getexif()

    creation_time = exif.get(36867)

    # noinspection PyBroadException
    try:
        if creation_time is None:
            creation_time = img.info["Creation Time"]
        try:
            date_obj = datetime.strptime(creation_time,
                                         "%a %d %b %Y %H:%M:%S %z")
        except ValueError:
            creation_date = creation_time.split(' ')[0]
            creation_date = creation_date.split(':')
            creation_date.reverse()
            cre_date = '/'.join(creation_date)
            date_obj = datetime.strptime(cre_date, "%d/%m/%Y")

        formatted_date = date_obj.strftime(alt_date_format)
    except BaseException:
        return

    # Get Image Title from EXIF
    img_title = (exif.get(270, "").strip())

    rel_folders, _ = os.path.split(path)
    folders = rel_folders.split("/")
    cur_folder = folders[-1]
    dir_name = " ".join(cur_folder.split('_')[:-1])
    dir_name = dir_name.split("\\")[-1]

    meta_font, meta_width, meta_height = get_font_width_height(
        draw, creation_time, date_font_size
    )

    x_pos = cell_width
    y_pos = int((grid_size - 4) * cell_height)
    draw.text((x_pos, y_pos), formatted_date, fill=text_color,
              font=meta_font, stroke_width=3, stroke_fill="black")

    draw.text((x_pos, int((grid_size - 7) * cell_height)), dir_name,
              fill=text_color,
              font=meta_font, stroke_width=3, stroke_fill="black")

    meta_font, meta_width, meta_height = get_font_width_height(
        draw, img_title, int(date_font_size * 1.5))

    title_x = (grid_size / 2 * cell_width) - (meta_width / 2)
    title_y = ((grid_size - 1) * cell_height - meta_height)

    draw.text((title_x, title_y), img_title, fill=text_color, font=meta_font,
              stroke_width=3, stroke_fill="black")


def add_current_time_to_image(
        draw,
        cell_width,
        cell_height,
        time_format=TIME_FORMAT,
        date_format=DATE_FORMAT,
        grid_size=GRID_SIZE,
        text_color=TEXT_COLOR,
):
    display_time = time.strftime(time_format)
    display_date = date.today().strftime(date_format)

    font_info = get_font_info(draw, display_date, display_time,
                              cell_height * 3)

    time_font = font_info["time"]
    date_font = font_info["date"]
    date_font_size = font_info["date_font_size"]

    # Align time with end of date string
    width_offset = date_font["width"] - time_font["width"]
    offset = ((grid_size - 1) * cell_width) - date_font["width"]
    date_coord_x = offset
    date_coord_y = int((grid_size - 4) * cell_height)

    time_coord_x = date_coord_x + width_offset
    time_coord_y = date_coord_y - time_font["height"]

    draw.text((time_coord_x, time_coord_y), display_time, fill=text_color,
              font=time_font["font"], stroke_width=3, stroke_fill="black")

    draw.text((date_coord_x, date_coord_y), display_date, fill=text_color,
              font=date_font["font"], stroke_width=3, stroke_fill="black")

    return date_font_size, date_coord_x


def draw_grid(draw, cell_width, cell_height, img_width, img_height,
              grid_size=GRID_SIZE):
    for i in range(1, grid_size + 1):
        draw.line([(i * cell_width, 0), (i * cell_width, img_height)],
                  fill="purple",
                  width=5)
        draw.line([(0, i * cell_height), (img_width, i * cell_height)],
                  fill="purple",
                  width=5)


def get_font_width_height(draw, ink, font_size, ratio=1,
                          font_path=FONT_PATH):
    try:
        font = ImageFont.truetype(font_path, int(
            font_size * ratio))
    except OSError:
        font = ImageFont.truetype("arial.ttf", int(
            font_size * ratio))

    width, height = draw.textsize(ink, font)

    return font, width, height


def get_font_info(draw, display_date, display_time, cell_height,
                  t2dr=TIME_TO_DATE_RATIO):
    date_font_size = 1

    date_font, date_width, date_height = get_font_width_height(
        draw, display_date, date_font_size
    )
    time_font, time_width, time_height = get_font_width_height(
        draw, display_time, date_font_size, ratio=t2dr
    )

    while date_height < cell_height:
        date_font_size += 1
        time_font, time_width, time_height = get_font_width_height(
            draw, display_time, date_font_size, ratio=t2dr
        )
        date_font, date_width, date_height = get_font_width_height(
            draw, display_date, date_font_size
        )

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

# def get_path_of_original_images(img_dir=IMG_DIR):
#     files = os.scandir(img_dir)
#
#     images = []
#     for file in files:
#         if file.is_dir():
#             if file.name in EXCLUDE_DIRS:
#                 pass
#             else:
#                 images += get_path_of_original_images(file.path)
#             continue
#         if file.name.endswith((".jpg", ".png", ".MP4")):
#             images.append(f"{img_dir}/{file.name}")
#
#     return images
