# Dailies Tool

The **Dailies Tool** is designed for VFX, animation, and film production to help create video files and image sequences from input image sequences, typically in EXR format. This tool supports operations like:

- **Creating videos** from image sequences (e.g., EXR to QT or other formats).
- **Converting between image sequence formats** (e.g., EXR to JPG).
- **Downscaling image resolutions** for easier review or delivery.

Users can also input metadata related to the video, select render settings, and leverage various external video engines like **FFmpeg**, **Nuke**, and **RV** to perform the processing.

This tool is primarily intended for creating dailies, but can be adapted to other use cases where image sequences need to be processed and video files need to be generated.

## Features

- **Video Creation**: Generate video files from image sequences (e.g., EXR, PNG, JPG).
- **Image Sequence Conversion**: Convert between different image sequence formats (e.g., EXR to JPG, etc.).
- **Resolution Adjustment**: Downscale or upscale the resolution of image sequences or videos.
- **Slate Generation**: Optionally add a slate (metadata overlay) to videos or image sequences, with customizable fields like project name, artist, version, etc.
- **Tracking Software Integration**: Automatically integrate with tracking software like **Shotgun**, **Ftrack**, **Kitsu**, and **Flow** for version management.

## Installation Instructions

### 1. **Install Python Dependencies**:
To install the required Python packages for the application, run the following command:

```bash
pip install -r requirements.txt
```

### 2. **Install External Software**:
The following external software must be installed separately. Ensure that these executables are accessible from your system's `PATH`.

- **FFmpeg**: Download and install FFmpeg from the official website: [FFmpeg Downloads](https://ffmpeg.org/download.html)
  - Once installed, ensure that the `ffmpeg.exe` file is in your system's `PATH`.

- **Nuke**: Nuke is a proprietary software. Please download and install it from the official website: [Nuke Downloads](https://www.foundry.com/products/nuke)
  - Ensure that the `nuke` executable and Python bindings are available and accessible from your environment.

- **RV**: RV is also proprietary software. Install it from [RV Downloads](https://www.foundry.com/products/rv)
  - Ensure the `rv` executable is added to your system's `PATH`.

### 3. **Modify `constants.py`**:
The `constants.py` file contains essential configuration information, including API URLs and authentication tokens for the tracking software. You must update the following fields accordingly:

- **Tracking Software Configuration**: Specify the tracking engine you wish to use (e.g., **Shotgun**, **Ftrack**, **Kitsu**, **Flow**) by setting the `TRACKING_ENGINE` variable.
- **API URLs**: Update the API URLs for the tracking systems in the `API_URLS` dictionary.
- **API Token**: Ensure the `API_TOKEN` and `PROJECT_ID` are set with the correct values to authenticate with your chosen tracking software.

### 4. **Ensure Correct Path Configuration**:
Make sure that the paths to the executables for **FFmpeg**, **Nuke**, and **RV** are correctly set in your system's environment variables so that they can be accessed from anywhere.
