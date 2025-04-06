import json
import os
import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH, DEFAULT_PRESET_DIRECTORY

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE_PATH),
    ],
)


def load_presets_from_folder(folder_path=DEFAULT_PRESET_DIRECTORY):
    """
    Loads all preset data from JSON files in the given folder.

    :param folder_path: Path to the folder containing preset JSON files.
    :return: Dictionary containing the preset configurations, keyed by preset name.
    """
    presets = {}

    if not os.path.isdir(folder_path):
        raise FileNotFoundError(
            f"The presets folder at {folder_path} does not exist or is not a directory."
        )

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            preset_name = filename.replace(".json", "")  # Use filename as preset name
            preset_file_path = os.path.join(folder_path, filename)

            try:
                with open(preset_file_path, "r") as file:
                    preset_data = json.load(file)
                    presets[preset_name] = preset_data
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON in preset {filename}: {e}")

    return presets
