import os

# import logging

# LOG_FILENAME = 'logging.out'
# logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
#                     datefmt="%Y-%m-%d %H:%M:%S")

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
    SLIDESHOW_DELAY = 2

EXCLUDE_DIRS = [
    "Videos_2020"
]

TIME_FORMAT = "%H:%M"  # e.g. 18:32
DATE_FORMAT = "%a %#d %b"  # e.g Sun 16 Aug
ALT_DATE_FORMAT = "%#d %b %Y"  # 6 Nov 2018

if ON_LINUX:
    FONT_PATH = "/usr/share/fonts/dejavu/DejaVuSans.ttf"
else:
    FONT_PATH = "/usr/share/fonts/dejavu/arial.ttf"

# rgba
TEXT_COLOR = (255, 255, 255, 255)  # white

SHOW_GRID = True
GRID_SIZE = 60
TIME_TO_DATE_RATIO = 2

BRISBANE_LAT = -27.4698
BRISBANE_LON = 153.0251

DAYBORO_LAT = -27.1962
DAYBORO_LONG = 152.8243

EXCLUDE = "minutely"

# noinspection SpellCheckingInspection
API_TOKEN = "d1414e08ebfc105903662cc153faf764"
API_URL_BASE = "https://api.openweathermap.org"
# noinspection SpellCheckingInspection
API_URL = f"{API_URL_BASE}/data/2.5/onecall?lat={DAYBORO_LAT}&lon" \
          f"={DAYBORO_LONG}&exclude={EXCLUDE}&appid={API_TOKEN}"

WEATHER_ICONS = {
    "01d": "clear_day",
    "01n": "clear_night",
    "02d": "few_clouds_day",
    "02n": "few_clouds_night",
    "03d": "cloudy",
    "03n": "cloudy",
    "04d": "cloudy",
    "04n": "cloudy",
    "09d": "rain",
    "09n": "rain",
    "10d": "rain",
    "10n": "rain",
    "11d": "thunderstorm",
    "11n": "thunderstorm",
    "50d": "mist",
    "50n": "mist",
}
