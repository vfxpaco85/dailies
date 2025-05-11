# Setup Instructions for Dailies Tool

## Introduction
This document provides setup instructions for the **Dailies Tool**, a utility for creating videos and image sequences from given image sequence paths, often used in VFX, animation, or film production. The tool allows users to take image sequences (e.g., EXR) and convert them into videos (e.g., QT) or other image formats (e.g., JPG), with options to downsize resolution, change format, or apply other transformations.

## Prerequisites

Before setting up the Dailies Tool, make sure you have the following installed:

- **Python 3.x**: Required to run the tool.
- **FFmpeg**: For video processing and conversion.
- **Nuke**: For advanced compositing and other VFX/animation tasks.
- **RV**: For reviewing and playback of sequences.

You also need access to the repository containing the Dailies Tool source code.

## 1. **Clone the Repository**:
First, clone the repository to your local machine. You can do this using Git:

```bash
git clone https://your-repository-url.git
cd your-repository-folder
```

## 2. **Install Python Dependencies**:
To install the required Python packages for the application, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

This will install all the necessary Python libraries the Dailies Tool depends on.

## 3. **Install External Software**:
The following external software must be installed separately. Ensure that these executables are accessible from your system's `PATH`.

- **FFmpeg**: Download and install FFmpeg from the official website: [FFmpeg Downloads](https://ffmpeg.org/download.html)
  - Once installed, ensure that the `ffmpeg.exe` file is in your system's `PATH`.

- **Nuke**: Nuke is a proprietary software. Please download and install it from the official website: [Nuke Downloads](https://www.foundry.com/products/nuke)
  - Ensure that the `nuke` executable and Python bindings are available and accessible from your environment.

- **RV**: RV is also proprietary software. Install it from [RV Downloads](https://www.foundry.com/products/rv)
  - Ensure the `rv` executable is added to your system's `PATH`.

## 4. **Ensure Correct Path Configuration**:
Make sure that the paths to the executables for **FFmpeg**, **Nuke**, and **RV** are correctly set in your system's environment variables so that they can be accessed from anywhere.

## 5. **Modify the `constant.main.py` and `constant.tracking.py` Files**:
The Dailies Tool relies on certain configurations that should be set in the `constant` module files. These include paths, credentials, and other system-specific information. 

### `constant.main.py`
The `constant.main.py` file defines core settings for logging, temporary directories, and slate templates.

Ensure the following values are correctly configured:

```python
# Set the log file path
LOG_FILE_PATH = "C:/code/python/vfx/dailies/dailies_tool.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Temporary file directory
BASE_TMP_DIRECTORY = "C:/Users/info/AppData/Local/Temp"
DEFAULT_TMP_DIRECTORY = get_daily_tmp_directory(BASE_TMP_DIRECTORY)

# Preset and template directories
DEFAULT_PRESET_DIRECTORY = "C:/code/python/vfx/dailies/preset"
DEFAULT_TEMPLATE_DIRECTORY = "C:/code/python/vfx/dailies/template"

# Environment variable configuration
ENV_VAR_CONFIG = {
    "path": "VIDEO_PATH",
    "version": "VERSION_NAME",
    "link": "LINK_NAME",
    "description": "DESCRIPTION",
    "artist": "ARTIST",
    "task": "TASK",
    "project": "PROJECT",
    "project_id": "PROJECT_ID",
    "entity_name": "ENTITY_NAME",
    "entity_id": "ENTITY_ID",
    "entity_type": "ENTITY_TYPE",
    "artist_name": "ARTIST_NAME",
    "artist_id": "ARTIST_ID",
}

# Frame padding and start number
FRAME_PADDING_FORMAT = '%03d'
FRAME_START_NUMBER = '001'

# Slate template for generating slate information
DEFAULT_SLATE_TEMPLATE = """
VERSION: {version}
FILE: {file}
DESCRIPTION: {description}
ARTIST: {artist}
LINK: {link}
TASK: {task}
PROJECT: {project}
RESOLUTION: {resolution}
FPS: {fps}
"""
```

### `constant.tracking.py`
The `constant.tracking.py` file defines the configuration for tracking software, API credentials, and the tracking engine to use.

Ensure the following values are correctly configured:

```python
# Tracking engine settings
TRACKING_ENGINE = os.getenv("TRACKING_ENGINE", "shotgun")
TRACKING_LOGIN_USER = os.getenv("TRACKING_LOGIN_USER", "USR")
TRACKING_API_TOKEN = os.getenv("TRACKING_API_TOKEN", "PWD")

# API URLs for tracking engines
API_URLS = {
    "shotgun": "https://your-shotgun-instance.com/api/v1",
    "ftrack": "https://your-ftrack-instance.com/api/v1",
    "kitsu": "https://your-kitsu-instance.com/api/v1",
    "flow": "https://your-flow-instance.com/api/v1",
}

```

## 6. **Running the Tool**:
Once the setup is complete, you can start using the Dailies Tool to create videos and image sequences from your input image sequences.

- **Run the Tool**: You can launch the tool by running the following command from the project directory:

```bash
python dailiy.py
```

- **Specify Input Path**: When prompted, provide the path to your input image sequence or EXR files.

- **Choose Output Settings**: You’ll be asked to choose the output format (such as EXR, JPG, or video) and other render settings (e.g., downsize resolution, frame rate adjustments).

- **Select External Engine**: Choose the appropriate external software (e.g., FFmpeg, Nuke, RV) for processing the output.

## 7. **Updating the Tool**:
If you need to update or add new features, follow these steps:
- Pull the latest changes from the repository.
- Install any new dependencies by running:

```bash
pip install -r requirements.txt
```

- Update configuration files as necessary (e.g., `constant.main.py`, `constant.tracking.py`, `constant.engine.py`).

## 8. **Troubleshooting**:
If you encounter any issues, make sure the following checks are done:

- Verify that your external tools (FFmpeg, Nuke, RV) are installed correctly and accessible from the `PATH`.
- Ensure that the `constant` files have been modified to include the correct paths, API keys, or other project-specific information.
- If the tool doesn’t run as expected, try checking the error logs or console output for more detailed information.

---

With these instructions, you should be able to run and configure the Dailies Tool. If you encounter any issues, refer to the troubleshooting section for guidance, or feel free to consult the project's README for more details.
