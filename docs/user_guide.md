# User Guide for Dailies Tool UI

The **Dailies Tool** UI provides an easy-to-use interface for entering project information, artist information and render settings. This guide will walk you through the features and how to interact with the tool.

## Features

### 1. **Input Fields for Video Information**
The form allows users to input essential metadata related to the video or image sequence being processed. The following fields are available:

- **Path**: Enter the path to the image sequence or video file. Use the **Browse** button to open a file dialog and select the file.
- **Version Name**: Enter a version name for the video or image sequence.
- **Description**: A text field to enter a brief description of the video or image sequence.
- **Artist**: The name of the artist responsible for this version of the file.
- **Link**: A link related to the file or project, such as a URL to a project or a reference document.
- **Task**: The specific task the video or image sequence corresponds to.
- **Project**: The name of the project the video or image sequence is part of.

### 2. **Render Settings**
The **Render Settings** section includes various fields for selecting render options and configuring the output format.

- **Preset**: Choose from available presets or select "None" to customize settings manually.
- **Engine**: Select the engine to use for rendering (FFmpeg, Nuke, NukeTemplate, or RVIO).
- **FPS**: Enter the frames per second for the output.
- **Resolution**: Specify the resolution for the output file.
- **Codec**: Enter the codec to use for encoding.
- **Extension**: Specify the file extension for the output files (e.g., `.mp4`, `.exr`).
- **Slate**: Enable or disable slate (usually used for preview purposes in the VFX industry).
- **Template**: For the "NukeTemplate" engine, specify a path to a Nuke template file. The "Browse..." button allows you to select the template from your file system.

### 3. **File Dialogs**
- **Browse Button**: The "Browse..." button allows you to select the image sequence or video file through a file dialog. It is available next to the "Path" field.
- **Template Browse Button**: For NukeTemplate engine, the "Browse..." button allows you to select a Nuke template file.

### 4. **Submit Button**
Once all the required fields are filled, clicking the **Submit** button will log all the input data. This helps to keep track of the user's selections for debugging and tracking purposes.

## Getting Started

Follow these steps to use the **Dailies Tool** UI:

### 1. **Launching the Tool**
To launch the Dailies Tool UI, ensure you have the necessary dependencies installed and your environment set up correctly.

Run the following command to start the tool:

```bash
# Run this command to launch the Dailies Tool UI
python ui.py
```

The UI window will appear, and you can start filling out the form.

### 2. **Filling Out the Form**

- **Path**: Click the **Browse** button next to the **Path** field to open a file dialog and select your video or image sequence.
- **Version Name**: Enter the version name of the video/image sequence.
- **Description**: Provide a short description of the video or image sequence.
- **Artist**: Enter the name of the artist responsible for the current file.
- **Link**: Add a relevant link, such as a project link or reference URL.
- **Task**: Enter the task associated with the video or image sequence.
- **Project**: Enter the project name to which the video or image sequence belongs.

### 3. **Choosing Render Settings**

- **Preset**: If available, select a preset from the dropdown. The options will load based on predefined settings in the **presets** folder.
- **Engine**: Choose the rendering engine. Available engines include:
  - **FFmpeg**: The default option for video encoding.
  - **Nuke**: Use this option for Nuke-specific workflows.
  - **NukeTemplate**: Use a Nuke template for rendering.
  - **RVIO**: Use this for RVIO-based workflows.
- **FPS**: Specify the FPS for the render.
- **Resolution**: Define the resolution for the output.
- **Codec**: Choose the codec for the output file (e.g., H.264, ProRes).
- **Extension**: Select the file extension (e.g., `.mp4`, `.jpg`, `.exr`).
- **Slate**: Check the **Slate** box if you want a slate to be added to the output.
- **Template**: If you're using the **NukeTemplate** engine, you can choose a template file using the **Browse** button.

### 4. **Submitting the Form**

Once all the fields are filled out, click the **Submit** button to log the provided data. This will help track the input information for debugging and reference purposes. The submitted data is logged to both the console and a log file.

## Troubleshooting

If you encounter any issues with the Dailies Tool UI, refer to the [Troubleshooting Guide](troubleshooting.md) for solutions to common problems.

## Code Overview

Here’s an overview of the relevant code for interacting with the tool:

### 1. **Setting Up the Logging**
The logging configuration is set up at the beginning of the `ui.py` file. This ensures that all user input is logged for debugging and tracking.

```python
# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level to INFO
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler(LOG_FILE_PATH)  # Log to the log file
    ]
)
```

### 2. **Creating the UI**
The UI is created using **PySide6**, a Python binding for Qt. The layout is composed of multiple input fields, dropdowns, and buttons, as described earlier.

```python
# Example UI layout for form and render settings
form_layout = QFormLayout()
self.path_input = QLineEdit(self)  # Path input field
self.browse_button = QPushButton("Browse...", self)  # Browse button
self.browse_button.clicked.connect(self.browse_file)  # Connect to file dialog
```

### 3. **Handling Form Submission**
When the user clicks the **Submit** button, the form data is logged, and the application is ready for the next operation.

```python
def on_submit(self):
    """Handles the submission of the form data, logging all fields."""
    # Collect user input and log it
    logging.info(f"Path: {path}")
    logging.info(f"Version Name: {version}")
    logging.info(f"Description: {description}")
    # Log all other input fields...
    logging.info("Data submitted successfully!")
```

---

For more advanced usage, custom presets can be created and stored in the **presets** folder. These presets are loaded when the tool starts up and can be selected from the **Preset** dropdown.

If you have additional questions or need further assistance, please refer to the [Troubleshooting Guide](troubleshooting.md).
