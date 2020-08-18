import os

IMAGES_DIR = "/media/usb/images/Iceland_2019"
CAPTION_DIR = "captions"

IMAGE_FILE_EXTENSIONS = ["jpg", "png"]


def get_sub_directories(path):
    """Returns list of directories within path"""
    sub_directories = []
    for file in os.scandir(path):
        if file.is_dir():
            sub_directories.append(file)

    return sub_directories


def is_valid_dir(directory):
    """
    A valid directory ends with the year to be displayed in the caption.

    An invalid directory for example would be the "captions" directory.
    """
    dir_parts = directory.name.split("_")
    if len(dir_parts) >= 2:
        last_part = dir_parts[-1]
        try:
            int(last_part)
            return True
        except ValueError:
            return False
    else:
        return False


def ensure_captions_dir_exists(directory):
    """If 'captions' does not exits, create it in the directory."""
    if not os.path.exists(f"{directory.path}/{CAPTION_DIR}"):
        os.makedirs(f"{directory.path}/{CAPTION_DIR}")


def create_captions(directory):
    """Create caption for each image within the directory"""
    files_in_directory = os.listdir(directory.path)

    for file in files_in_directory:
        file_extension = file.split(".")[-1]
        if file_extension in IMAGE_FILE_EXTENSIONS:
            image_caption_file = open(
                f"{directory.path}/{CAPTION_DIR}/{file}.txt",
                "w")
            caption = directory.name.replace("_", " ")
            image_caption_file.write(f"  {caption}  ")


def main(path):
    """
    This will recursively search sub_directories in 'path' and create the
    captions text file for each image it finds.
    """
    sub_directories = get_sub_directories(path)
    for directory in sub_directories:
        main(directory.path)
        if is_valid_dir(directory):
            ensure_captions_dir_exists(directory)
            create_captions(directory)


if __name__ == '__main__':
    main(IMAGES_DIR)
