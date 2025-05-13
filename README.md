# Dailies Tool

The **Dailies Tool** is designed for VFX, animation, and film production to help create video files and image sequences from input image sequences, typically in EXR format. This tool supports operations like:

- **Creating videos** from image sequences (e.g., EXR to QT or other formats).
- **Converting between image sequence formats** (e.g., EXR to JPG).
- **Downscaling image resolutions** for easier review or delivery.

Users can also input project and artist information, select render settings, and leverage various external video engines like **FFmpeg**, **Nuke**, and **RV** to perform the processing.

This tool is primarily intended for creating dailies and submitting into a tracking software (**Shotgun**, **Ftrack**, and **Kitsu**), but can be adapted to other use cases where image sequences or videos need to be processed and media files need to be generated. It is essentially a wrapper around **FFmpeg**, **Nuke**, and **RV**.

## Features

- **Video Creation**: Generate video files from image sequences (e.g., EXR, PNG, JPG).
- **Image Sequence Creation**: Generate image sequences from video files (e.g., MOV to JPG, etc.).
- **Image Sequence Conversion**: Convert between different image sequence formats (e.g., EXR to JPG, etc.).
- **Resolution Adjustment**: Downscale or upscale the resolution of image sequences or videos.
- **Slate Generation**: Optionally add a slate frame at the beginning of videos or image sequences, displaying customizable info like project name, artist, version, etc.
- **Tracking Software Integration**: Automatically integrate with tracking software like **Shotgun**, **Ftrack**, and **Kitsu** for version management.

## Installation Instructions

### 1. **Install Python Dependencies**:
To install the required Python packages for the application, run the following command:

```bash
pip install .
```

### 2. **Install External Software**:
The following external software must be installed separately. Ensure that these executables are accessible from your system's `PATH`.

- **FFmpeg**: Download and install FFmpeg from the official website: [FFmpeg Downloads](https://ffmpeg.org/download.html)
  - Once installed, ensure that the `ffmpeg.exe` file is in your system's `PATH`.

- **Nuke**: Nuke is a proprietary software. Please download and install it from the official website: [Nuke Downloads](https://www.foundry.com/products/nuke)
  - Ensure that the `nuke` executable and Python bindings are available and accessible from your environment.

- **RV**: RV is also proprietary software. Install it from [RV Downloads](https://www.autodesk.com/products/flow-production-tracking/rv)
  - Ensure the `rv` executable is added to your system's `PATH`.

### 3. **Ensure Executables Are in Your System PATH**:
Make sure the executables for **FFmpeg**, **Nuke**, and **RV** are accessible from your system’s `PATH`. This allows the tool to invoke them from anywhere.

### 4. **Modify Tracking Constant Module**:
The `dailies.constant.tracking.py` file contains essential configuration information for the tracking software. You must update the following fields accordingly:

- **Tracking Software Configuration**: Specify the tracking engine you wish to use (e.g., **Shotgun**, **Ftrack**, **Kitsu**) by setting the `TRACKING_ENGINE` variable.
- **API URLs**: Update the API URLs for the tracking systems in the `API_URLS` dictionary.
- **API Token**: Ensure the `TRACKING_API_TOKEN` is set with the correct values to authenticate with your chosen tracking software.
- **API User**: Ensure the `TRACKING_LOGIN_USER` set with the correct values to authenticate with your chosen tracking software.

### 5. **Ensure Correct PYTHON_PATH Configuration:**
To ensure that the tool can access necessary modules and resources, you need to set the correct path for your project directory in the `PYTHON_PATH` environment variable.

You can add the project directory to your `PYTHON_PATH` by running the following command:

#### On Linux/macOS:

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
```

#### On Windows:

```bash
set PYTHONPATH=%cd%;%PYTHONPATH%
```

Alternatively, you can add this line to your shell configuration file (e.g., `.bashrc`, `.zshrc`, or `.bash_profile` on macOS/Linux) or system environment variables on Windows for persistent access.


## Build the docs locally

```python
pip install mkdocs mkdocs-material
mkdocs serve
```
