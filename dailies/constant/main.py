import os
import tempfile

from dailies.constant.util import get_daily_tmp_directory, get_package_root_directory

# Define the log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Define the log file path using os.path.join and relative to the package location
LOG_FILE_PATH = os.path.join(get_package_root_directory(), 'dailies.log')

# Default directories for presets and templates (relative to the package location)
# These will work well for a quick test but should be modified with proper path in studio environment setup.
DEFAULT_PRESET_DIRECTORY = os.path.join(get_package_root_directory(), 'preset')
DEFAULT_TEMPLATE_DIRECTORY = os.path.join(get_package_root_directory(), 'template')

# Get the system's base temporary directory (cross-platform)
BASE_TMP_DIRECTORY = tempfile.gettempdir()

# Use the utility function to generate the path for the daily TMP directory.
# This directory will be used to store daily-specific temporary files.
DEFAULT_TMP_DIRECTORY = get_daily_tmp_directory(BASE_TMP_DIRECTORY)

# Dictionary mapping common field names to corresponding environment variable names.
# This is useful for extracting values from environment variables dynamically.
ENV_VAR_CONFIG = {
    "path": "VIDEO_PATH",             # The path to the video file
    "version": "VERSION_NAME",        # The version name of the media
    "description": "DESCRIPTION",     # A description of the media or task
    "project": "PROJECT",             # The project name
    "project_id": "PROJECT_ID",       # The unique ID for the project
    "entity_name": "ENTITY_NAME",     # The name of the entity (e.g., shot, asset, etc.)
    "entity_id": "ENTITY_ID",         # The unique ID for the entity
    "entity_type": "ENTITY_TYPE",     # The type of entity (e.g., shot, asset)
    "task_name": "TASK_NAME",         # The name of the task
    "task_id": "TASK_ID",             # The unigque ID for the task
    "artist_name": "ARTIST_NAME",     # The name of the artist
    "artist_id": "ARTIST_ID",         # The unique ID for the artist
}

# Frame padding format to ensure consistent frame numbering (e.g., "001", "002", "003", etc.).
# This will be used to format frame numbers with leading zeros.
FRAME_PADDING_FORMAT = '%03d'  # This means three digits with leading zeros, like "001"

# The starting frame number for sequences.
# This value can vary depending on the users/company's setup.
# For example, it can be '001', '1001', or any other starting point.
FRAME_START_NUMBER = '001'  # Default starting frame number for sequences

# Default template for slate generation, which contains placeholder fields to be filled dynamically.
# The template includes fields for version, file name, description, artist, task, project, resolution, and FPS.
DEFAULT_SLATE_TEMPLATE = """
VERSION: {version}
FILE: {file}
DESCRIPTION: {description}
ARTIST: {artist}
LINK: {link}
TASK: {task}
PROJECT: {project}
RESOLUTION: {resolution[0]}x{resolution[1]}
FPS: {fps}
"""
