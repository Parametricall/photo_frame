# import os
# import time
# import random
# from datetime import date, datetime
#
# from PIL import Image, ImageDraw, ImageFont
#
#
# # IMG_DIR = "./media/usb/images/Iceland_2019"
# #
# # DISPLAY_DIR = "display_photo"
# # DISPLAY_IMAGE_NAME = "output.jpg"
# # DISPLAY_IMG_TYPE = "JPEG"
# #
# # TIME_FORMAT = "%H:%M"  # e.g. 18:32
# # DATE_FORMAT = "%a %#d %b"  # e.g Sun 16 Aug
# # ALT_DATE_FORMAT = "%#d %b %Y"  # 6 Nov 2018
# #
# # if os.path.exists("/usr/share/fonts"):
# #     font_path = "/usr/share/fonts"
# # else:
# #     font_path = ""
# #
# # FONT_PATH = "f{font_path}/dejavu/DejaVuSans.ttf"
# # # TIME_FONT_SIZE = 175
# # # DATE_FONT_SIZE = 100
# #
# # TIME_FONT_SIZE = 125
# # DATE_FONT_SIZE = 50
# #
# # # rgba
# # TEXT_COLOR = (255, 255, 255, 255)  # white
# #
# # SLEEP_TIME = 5
# #
# # SHOW_GRID = False
# # GRID_SIZE = 20
# # TIME_TO_DATE_RATIO = 2
#
#
# def check_or_create_display_dir():
#     if not os.path.exists(DISPLAY_DIR):
#         os.makedirs(DISPLAY_DIR)
#
#
# def get_font_width_height(draw, ink, font_size, font_path, ratio=1):
#     try:
#         font = ImageFont.truetype(font_path, int(
#             font_size * ratio))
#     except OSError:
#         font = ImageFont.truetype("arial.ttf", int(
#             font_size * ratio))
#
#     width, height = draw.textsize(ink, font)
#
#     return font, width, height
#
#
# def get_font_info(draw, display_date, display_time, cell_height,
#                   font_path, ratio):
#     date_font_size = 1
#
#     date_font, date_width, date_height = get_font_width_height(
#         draw, display_date, date_font_size, font_path
#     )
#     time_font, time_width, time_height = get_font_width_height(
#         draw, display_time, date_font_size, font_path, ratio=ratio
#     )
#
#     while date_height < cell_height:
#         time_font, time_width, time_height = get_font_width_height(
#             draw, display_time, date_font_size, font_path, ratio=ratio
#         )
#         date_font, date_width, date_height = get_font_width_height(
#             draw, display_date, date_font_size, font_path
#         )
#         date_font_size += 1
#
#     return {
#         "time": {
#             "font": time_font,
#             "width": time_width,
#             "height": time_height,
#         },
#         "date": {
#             "font": date_font,
#             "width": date_width,
#             "height": date_height,
#         },
#         "date_font_size": date_font_size,
#     }
#
#
# def add_current_time_to_image(
#         draw,
#         cell_width,
#         cell_height,
#         time_format,
#         date_format,
#         time_to_date_ratio,
#         text_color,
#         font_path,
#         grid_size,
# ):
#     display_time = time.strftime(time_format)
#     display_date = date.today().strftime(date_format)
#
#     font_info = get_font_info(draw, display_date, display_time, cell_height,
#                               font_path, ratio=time_to_date_ratio)
#
#     time_font = font_info["time"]
#     date_font = font_info["date"]
#     date_font_size = font_info["date_font_size"]
#
#     # Align time with end of date string
#     width_offset = date_font["width"] - time_font["width"]
#     offset = ((grid_size - 1) * cell_width) - date_font["width"]
#     date_coord_x = offset
#     date_coord_y = int((grid_size - 2) * cell_height)
#
#     time_coord_x = date_coord_x + width_offset
#     time_coord_y = date_coord_y - time_font["height"] - 2
#
#     print(f"date font = {date_font_size}")
#
#     draw.text((time_coord_x, time_coord_y), display_time, fill=text_color,
#               font=time_font["font"], stroke_width=3, stroke_fill="black")
#     draw.text((date_coord_x, date_coord_y), display_date, fill=text_color,
#               font=date_font["font"], stroke_width=3, stroke_fill="black")
#
#     return date_font_size
#
#
# def show_grid(draw, grid_size, cell_width, cell_height, img_width, img_height):
#     for i in range(1, grid_size + 1):
#         draw.line([(i * cell_width, 0), (i * cell_width + 10, img_height)],
#                   fill="purple",
#                   width=5)
#         draw.line([(0, i * cell_height), (img_width, i * cell_height + 10)],
#                   fill="purple",
#                   width=5)
#
#
# def is_valid_dir(directory):
#     """
#     A valid directory ends with the year to be displayed in the caption.
#
#     An invalid directory for example would be the "captions" directory.
#     """
#     dir_parts = directory.name.split("_")
#     if len(dir_parts) >= 2:
#         last_part = dir_parts[-1]
#         try:
#             int(last_part)
#             return True
#         except ValueError:
#             return False
#     else:
#         return False
#
#
# def add_location_and_year(
#         draw,
#         img,
#         path,
#         cell_width,
#         cell_height,
#         date_font_size,
#         date_format,
#         text_color,
#         font_path,
#         grid_size,
#         img_dir_path,
# ):
#     exif = img.getexif()
#
#     creation_time = exif.get(36867)
#     creation_date = creation_time.split(' ')[0]
#     creation_date = creation_date.split(':')
#     creation_date.reverse()
#     date = '/'.join(creation_date)
#
#     date_obj = datetime.strptime(date, "%d/%m/%Y")
#
#     formatted_date = date_obj.strftime(date_format)
#
#     directory_path = path.replace(img_dir_path, "")
#
#     rel_folders, _ = os.path.split(directory_path)
#     folders = rel_folders.split("/")
#     cur_folder = folders[-1]
#     dir_name = " ".join(cur_folder.split('_')[:-1])
#     dir_name = dir_name.replace("\\", "")
#
#     meta_font, meta_width, meta_height = get_font_width_height(
#         draw, creation_time, date_font_size, font_path
#     )
#
#     x_pos = cell_width
#     y_pos = int((grid_size - 2) * cell_height)
#     draw.text((x_pos, y_pos), formatted_date, fill=text_color,
#               font=meta_font, stroke_width=3, stroke_fill="black")
#
#     draw.text((x_pos, int((grid_size - 3) * cell_height)), dir_name,
#               fill=text_color,
#               font=meta_font, stroke_width=3, stroke_fill="black")
#
#
# def get_path_of_original_images(img_dir):
#     files = os.scandir(img_dir)
#
#     images = []
#     for file in files:
#         if file.is_dir():
#             images += get_path_of_original_images(file.path)
#             continue
#         if file.name.endswith(".jpg"):
#             images.append(f"{img_dir}/{file.name}")
#
#     return images
#
#
# if __name__ == '__main__':
#     original_image_paths = get_path_of_original_images()
#     randomised_image_paths = list(range(len(original_image_paths)))
#     random.shuffle(randomised_image_paths)
#
#     while True:
#         for image_path_index in randomised_image_paths:
#             current_time = time.strftime(TIME_FORMAT)
#             current_date = date.today().strftime(DATE_FORMAT)
#             image_path = original_image_paths[image_path_index]
#
#             image = Image.open(image_path).convert(
#                 "RGB")
#             draw = ImageDraw.Draw(image)
#             date_font_size = add_current_time_to_image(draw, image,
#                                                        current_time,
#                                                        current_date)
#             add_location_and_year(draw, image, image_path, date_font_size)
#
#             check_or_create_display_dir()
#             image.save(f"{DISPLAY_DIR}/{DISPLAY_IMAGE_NAME}", DISPLAY_IMG_TYPE)
#             time.sleep(SLEEP_TIME)
