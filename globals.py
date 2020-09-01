import os

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
