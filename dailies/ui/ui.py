import os
import logging
import re

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QCheckBox,
    QMessageBox,
)

from dailies.constant.main import (
    LOG_FORMAT,
    LOG_FILE_PATH,
    DEFAULT_TEMPLATE_DIRECTORY,
    FRAME_PADDING_FORMAT,
    FRAME_START_NUMBER,
)
from dailies.constant.engine import SUPPORTED_FILE_TYPES, IMAGE_SEQUENCES_FILE_TYPES
from dailies.constant.tracking import TRACKING_ENGINE
from dailies.environment import Environment
from dailies.factory import VideoEngineFactory, TrackingSoftwareFactory

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,  # Set the default logger level to INFO
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler(LOG_FILE_PATH),
    ],
)


class DailiesUI(QWidget):
    """UI for managing video & image rendering and tracking software options for vfx/animation workflow."""

    def __init__(self, environment=None, presets=None, parent=None):
        """
        Initializes the UI with fields for project, artist info and render settings.

        Args:
            environment (dict, optional): Instance of Environment to prefill form fields.
            presets (list, optional): List of render presets for the dropdown.
            parent (QWidget, optional): Parent widget to embed the UI inside another application.
        """
        super().__init__(parent)
        self.setWindowTitle("Dailies Tool")
        self.setGeometry(100, 100, 400, 600)
        self._setup_ui(presets)
        self._set_field_tooltips()

        self._is_error = False
        self.presets = presets
        self.environment = environment

        if environment:
            self.prefill_form(environment)

        self.update_render_settings()

    def _setup_ui(self, presets):
        """
        Sets up the layout and UI elements.

        Args:
            presets (list): List of render presets for the dropdown.
        """
        # Create form layout
        form_layout = QFormLayout()

        # Create file path input and "Browse" button to open the file dialog
        self.input_path = QLineEdit(self)
        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.clicked.connect(self._browse_file_input)

        # Create a horizontal layout for the input path and browse button
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.input_path)
        path_layout.addWidget(self.browse_button)

        # Create input fields for main project & artist information
        self.version_input = QLineEdit(self)
        self.description_input = QTextEdit(self)
        self.artist_input = QLineEdit(self)
        self.link_input = QLineEdit(self)
        self.task_input = QLineEdit(self)
        self.project_input = QLineEdit(self)

        # Create checkbox for Tracking aligned to the right
        self.tracking_checkbox = QCheckBox("Tracking", self)

        # Create a layout to push checkboxes to the right side
        tracking_checkbox_layout = QHBoxLayout()
        tracking_checkbox_layout.addStretch(1)
        tracking_checkbox_layout.addWidget(self.tracking_checkbox)

        # Add input fields to the form layout
        form_layout.addRow(QLabel("Path:"), path_layout)
        form_layout.addRow(QLabel("Version Name:"), self.version_input)
        form_layout.addRow(QLabel("Description:"), self.description_input)
        form_layout.addRow(QLabel("Artist:"), self.artist_input)
        form_layout.addRow(QLabel("Entity:"), self.link_input)
        form_layout.addRow(QLabel("Task:"), self.task_input)
        form_layout.addRow(QLabel("Project:"), self.project_input)
        form_layout.addRow(tracking_checkbox_layout)  # Tracking checkbox

        # Create render options group
        render_group = QGroupBox("Render Settings", self)
        render_layout = QFormLayout()

        # First, create input fields for Extension, Resolution, FPS, Options
        self.extension_input = QComboBox(self)
        self.resolution_input = QLineEdit(self)
        self.fps_input = QLineEdit(self)
        self.options_input = QLineEdit(self)

        # Create combo box for the preset options
        self.preset_input = QComboBox(self)
        self.preset_input.addItem("None")  # Add the "None" option
        for preset_name in presets:
            self.preset_input.addItem(preset_name)
        self.preset_input.currentTextChanged.connect(self.update_render_settings)

        # Create combo box for the engine selection
        self.engine_input = QComboBox(self)
        self.engine_input.addItem("FFmpeg")
        self.engine_input.addItem("Nuke")
        self.engine_input.addItem("Nuke-Template")
        self.engine_input.addItem("RVIO")
        self.engine_input.currentTextChanged.connect(self.update_render_settings)

        # Create template input field and button (visible only if 'NukeTemplate' engine is selected)
        self.template_input = QLineEdit(self)
        self.template_input.setObjectName("template_input")
        self.template_button = QPushButton("Browse...", self)
        self.template_button.clicked.connect(self._browse_file_nuke_template)

        # Create a horizontal layout for the template field and the browse button
        template_layout = QHBoxLayout()
        template_layout.addWidget(self.template_input)
        template_layout.addWidget(self.template_button)

        # Create output path input field and "Browse" button to open the file dialog
        self.output_path = QLineEdit(self)
        self.output_browse_button = QPushButton("Browse...", self)
        self.output_browse_button.clicked.connect(self._browse_file_output)

        # Create a horizontal layout for the output path input and browse button
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.output_path)
        output_path_layout.addWidget(self.output_browse_button)

        # Create checkbox for Slate, aligned to the right
        self.slate_checkbox = QCheckBox("Slate", self)

        # Create a layout to push checkboxes to the right side
        slate_checkbox_layout = QHBoxLayout()
        slate_checkbox_layout.addStretch(1)
        slate_checkbox_layout.addWidget(self.slate_checkbox)

        # Add render options to the layout
        render_layout.addRow(QLabel("Preset:"), self.preset_input)
        render_layout.addRow(QLabel("Engine:"), self.engine_input)

        self.extension_label = QLabel("Extension:")
        self.resolution_label = QLabel("Resolution:")
        self.fps_label = QLabel("FPS:")
        self.options_label = QLabel("Options:")
        self.template_label = QLabel("Template:")
        self.output_path_label = QLabel("Output Path:")

        render_layout.addRow(self.extension_label, self.extension_input)
        render_layout.addRow(self.resolution_label, self.resolution_input)
        render_layout.addRow(self.fps_label, self.fps_input)
        render_layout.addRow(self.options_label, self.options_input)
        render_layout.addRow(self.template_label, template_layout)
        render_layout.addRow(self.output_path_label, output_path_layout)
        render_layout.addRow(slate_checkbox_layout)

        render_group.setLayout(render_layout)

        # Create submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.on_submit)

        # Set the main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(render_group)
        main_layout.addWidget(self.submit_button)

        self.setLayout(main_layout)

    def _browse_file(self, title, filter, callback):
        """
        Opens a file dialog and sets the file path using the provided callback.

        Args:
            title (str): The title of the file dialog.
            filter (str): The file filter to apply in the dialog.
            callback (function): The callback to set the selected file path.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, title, "", filter)
        if file_path:

            file_extension = os.path.splitext(file_path)[1][1:].lower()
            if file_extension in IMAGE_SEQUENCES_FILE_TYPES:
                file_path = self._get_image_sequence_file_path(file_path)

            # Set the path input with the processed path
            callback(file_path.replace("\\", "/"))

    def _browse_file_input(self):
        """Opens a file dialog for selecting a file and sets the path for input."""
        self._browse_file("Select File", "All Files (*)", self.input_path.setText)

    def _browse_file_output(self):
        """Opens a file dialog for selecting an output file and sets the path."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "All Files (*)"
        )
        if file_path:

            file_extension = os.path.splitext(file_path)[1][1:].lower()
            if file_extension in IMAGE_SEQUENCES_FILE_TYPES:
                file_path = self._get_image_sequence_file_path(file_path)

            self.output_path.setText(file_path.replace("\\", "/"))

    def _browse_file_nuke_template(self):
        """Opens a file dialog for selecting a Nuke template and sets the path."""
        self._browse_file(
            "Select Slate Template", "Nuke Template (*.nk)", self.template_input.setText
        )

    def _create_media(
        self,
        engine,
        input_path,
        output_path,
        extension=None,
        resolution=None,
        fps=None,
        template=None,
        options=None,
        slate=None,
    ):
        """
        Creates media based on engine type.

        Args:
            engine (str): The engine to use (e.g., 'FFmpeg', 'Nuke', 'Nuke-Template', 'RVIO').
            input_path (str): The input file path.
            output_path (str): The output file path.
            extension (str, optional): The file extension (e.g., 'mov').
            resolution (tuple, optional): The resolution as (width, height).
            fps (int, optional): The frames per second.
            template (str, optional): The template path for 'Nuke-Template'.
            options (dict, optional): Additional options.
            slate (dict, optional): Additional slate data.
        """
        video_engine = VideoEngineFactory.get_video_engine(engine.lower())
        try:
            if engine == "Nuke-Template":
                video_engine.create_media(input_path, output_path, template)
            else:
                video_engine.create_media(
                    input_path,
                    output_path,
                    extension=extension,
                    resolution=resolution,
                    fps=fps,
                    options=options,
                    slate=slate,
                )
        except Exception as e:
            logger.error(f"Error during video creation: {e}")
            self._show_error("Submission Error", f"{e}")
            self._is_error = True

    def _create_tracking_version(self, version, output_path):
        """
        Handles tracking the version by calling the appropriate tracking software.

        Args:
            version (str): The version information to be inserted into the tracked media.
            output_path (str): The path to the output media that needs to be tracked.

        Raises:
            Exception: If an error occurs during version insertion, an exception will be logged
                      and the error is shown to the user.
        """
        tracking = TrackingSoftwareFactory.get_tracking_software(
            TRACKING_ENGINE, self._get_environment()
        )
        try:
            tracking.insert_version(
                version, output_path, self.description_input.toPlainText()
            )
        except Exception as e:
            logger.error(f"Error during version creation: {e}")
            self._show_error("Tracking Error", f"{e}")
            self._is_error = True

    def _get_environment(self):
        """
        Ensures a valid Environment instance exists by checking required fields.
        If any are missing, it re-creates the Environment using the UI values.

        Returns:
            Environment or None: A fully initialized Environment object or None on error.
        """
        if (
            not self.environment
            or not self.environment.project_name
            or not self.environment.entity_name
            or not self.environment.task_name
            or not self.environment.artist_name
        ):
            try:
                self.environment = Environment(
                    project_name=self.project_input.text(),
                    entity_name=self.link_input.text(),
                    task_name=self.task_input.text(),
                    artist_name=self.artist_input.text(),
                )
                self.environment.log_configuration()
            except Exception as e:
                logger.error(f"Failed to initialize environment: {e}")
                self._show_error("Environment Error", str(e))
                self._is_error = True
                return None

        return self.environment

    def _get_image_sequence_file_path(self, file_path):
        """
        Processes a file path for image sequences and replaces the frame number
        with a dynamically generated padding format based on the sequence.

        Args:
            path (str): The file path to be processed.

        Returns:
            str: The file path with the frame number replaced by the padding format.
        """
        # Check if the file path contains a sequence of numbers
        # Captures the name, number, and extension
        sequence_pattern = r"(\D+)(\d+)(\.\w+)$"
        match = re.match(sequence_pattern, file_path)

        if match:
            # Extract the frame number and calculate the padding length dynamically
            frame_number = match.group(2)
            padding_length = len(frame_number)
            padding_format = f"%0{padding_length}d"

            # Replace the frame number with the dynamic padding format
            file_path = file_path.replace(frame_number, padding_format)

        return file_path

    def _log_submission(self):
        """Logs the data from the form submission."""
        logger.info("*****************************************************************")
        logger.info(f"Path: {self.input_path.text()}")
        logger.info(f"Version: {self.version_input.text()}")
        logger.info(f"Description: {self.description_input.toPlainText()}")
        logger.info(f"Artist: {self.artist_input.text()}")
        logger.info(f"Link: {self.link_input.text()}")
        logger.info(f"Task: {self.task_input.text()}")
        logger.info(f"Project: {self.project_input.text()}")
        logger.info(f"Tracking: {self.tracking_checkbox.isChecked()}")
        logger.info("*****************************************************************")
        logger.info(f"Preset: {self.preset_input.currentText()}")
        logger.info(f"Engine: {self.engine_input.currentText()}")
        logger.info(f"FPS: {self.fps_input.text()}")
        logger.info(f"Resolution: {self.resolution_input.text()}")
        logger.info(f"Options: {self.options_input.text()}")
        logger.info(f"Template: {self.template_input.text()}")
        logger.info(f"Output Path: {self.output_path.text()}")
        logger.info(f"Slate: {self.slate_checkbox.isChecked()}")
        logger.info("*****************************************************************")

    def _set_fields_enabled(self, enabled):
        """
        Enables or disables fields based on the enabled argument.

        Args:
            enabled (bool): Whether the fields should be enabled or disabled.
        """
        self.engine_input.setEnabled(enabled)
        self.extension_input.setEnabled(enabled)
        self.resolution_input.setEnabled(enabled)
        self.fps_input.setEnabled(enabled)
        self.options_input.setEnabled(enabled)
        self.slate_checkbox.setEnabled(enabled)
        self.template_input.setEnabled(enabled)
        self.template_button.setEnabled(enabled)

    def _set_field_tooltips(self):
        """
        Sets helpful tooltips for each field in the UI to guide the user.
        """
        self.input_path.setToolTip("Select the input video or image file.")
        self.version_input.setToolTip(
            "Enter the version name of the media (e.g., 'foobar_v001')."
        )
        self.description_input.setToolTip(
            "Provide a brief description of the daily submission."
        )
        self.artist_input.setToolTip(
            "Enter the artist's name responsible for the media."
        )
        self.link_input.setToolTip(
            "Provide an entity name (e.g. asset, sequence or shot) for the daily."
        )
        self.task_input.setToolTip("Enter the task associated with this media.")
        self.project_input.setToolTip("Enter the project name.")
        self.tracking_checkbox.setToolTip(
            "Check this box to create a version for the entity in the tracking software."
        )
        self.preset_input.setToolTip("Select a render preset (if any).")
        self.engine_input.setToolTip(
            "Select the rendering engine to use (e.g., FFmpeg, Nuke)."
        )
        self.resolution_input.setToolTip(
            "Enter the resolution in the format 'width x height' (e.g., 1920x1080)."
        )
        self.fps_input.setToolTip(
            "Enter the FPS (Frames Per Second) for the media (e.g., 24)."
        )
        self.options_input.setToolTip(
            "Enter any additional options as key-value pairs (e.g., 'key=value')."
        )
        self.template_input.setToolTip("Select the Nuke template file.")
        self.output_path.setToolTip(
            "Select the output file path where the rendered media will be saved."
        )
        self.slate_checkbox.setToolTip(
            "Check this box if you want to generate a slate for the video."
        )

    def _show_error(self, title, message):
        """Displays an error message box."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)  # Change to Critical for error
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        return

    def _update_render_fields_visibility(self):
        """
        Updates visibility of render settings based on selected engine.
        """
        engine = self.engine_input.currentText()
        is_visible = engine != "Nuke-Template"

        # First update template fields visibility
        self.template_label.setVisible(not is_visible)
        self.template_input.setVisible(not is_visible)
        self.template_button.setVisible(not is_visible)

        # Second update the remaining render fields visibility
        self.extension_label.setVisible(is_visible)
        self.extension_input.setVisible(is_visible)
        self.resolution_label.setVisible(is_visible)
        self.resolution_input.setVisible(is_visible)
        self.fps_label.setVisible(is_visible)
        self.fps_input.setVisible(is_visible)
        self.options_label.setVisible(is_visible)
        self.options_input.setVisible(is_visible)
        self.slate_checkbox.setVisible(is_visible)

    def get_fps(self):
        """
        Retrieves and validates the FPS input.

        Returns:
            int or None: The FPS as an integer or None if invalid.
        """
        try:
            return int(self.fps_input.text()) if self.fps_input.text() else None
        except ValueError:
            logger.error(f"Invalid FPS: {self.fps_input.text()}.")
            self._show_error("Invalid FPS", "FPS should be an integer value.")
            self._is_error = True
            return None

    def get_resolution(self):
        """
        Retrieves and validates the resolution input.

        Returns:
            tuple or None: A tuple (width, height) or None if invalid.
        """
        try:
            width, height = map(int, self.resolution_input.text().split("x"))
            return (width, height)
        except ValueError:
            logger.error(f"Invalid resolution: {self.resolution_input.text()}.")
            self._show_error(
                "Invalid Resolution",
                "Resolution should be in the format 'width x height' (e.g., 1920x1080).",
            )
            self._is_error = True
            return None

    def get_options(self):
        """
        Retrieves and validates the options input into key-value pairs or standalone values.

        Returns:
            dict or None: A dictionary of key-value pairs or None if invalid.
        """
        options = {}
        options_input = self.options_input.text()

        if options_input:
            # Define a regex pattern to match key-value pairs and standalone values with spaces allowed
            pattern = r"([a-zA-Z0-9_]+=[^,]+|[a-zA-Z0-9_]+)(?:,([a-zA-Z0-9_]+=[^,]+|[a-zA-Z0-9_]+))*"

            if re.fullmatch(pattern, options_input):
                pairs = options_input.split(",")
                for pair in pairs:
                    pair = pair.strip()
                    if "=" in pair:
                        key, value = pair.split("=")
                        options[key.strip()] = value.strip()
                    else:
                        options[pair] = None
            else:
                self._show_error(
                    "Invalid Options",
                    "Options must be in the format 'key=value' or standalone values separated by commas.",
                )
                self._is_error = True
                return None

        return options if options else None

    def get_slate_data(self):
        """
        Collects and returns the slate data for video rendering or tracking.

        Returns:
            dict: A dictionary containing the collected slate data,
                  including version, file, description, artist, link, task,
                  project, resolution, and FPS.
        """
        slate_data = {}
        file_name = os.path.basename(self.input_path.text()).replace(
            FRAME_PADDING_FORMAT, FRAME_START_NUMBER
        )
        slate_data = {
            "version": self.version_input.text(),
            "file": file_name,
            "description": self.description_input.toPlainText(),
            "artist": self.artist_input.text(),
            "link": self.link_input.text(),
            "task": self.task_input.text(),
            "project": self.project_input.text(),
            "resolution": self.resolution_input.text(),
            "fps": int(self.fps_input.text()),
        }
        return slate_data

    def set_options(self, options):
        """
        Sets the options input field with a comma-separated string of key-value pairs or flags
        based on the provided options dictionary.

        Args:
            options (dict): A dictionary where keys are option names and values are either
                            None (for flags) or a string representing the option value.
        """
        options_str = []

        for key, value in options.items():
            if value is None:
                options_str.append(key)  # Just a flag if the value is None
            else:
                options_str.append(f"{key}={value}")  # Key=value pair

        self.options_input.setText(",".join(options_str))

    def on_submit(self):
        """
        Handles form submission and triggers video rendering and tracking.
        """
        self._is_error = False

        input_path = self.input_path.text()
        version = self.version_input.text()
        is_tracking = self.tracking_checkbox.isChecked()
        is_slate = self.slate_checkbox.isChecked()
        engine = self.engine_input.currentText()

        # FPS, resolution, options are only supported for 'Nuke', 'FFmpeg', 'RVIO' engine
        if engine != "Nuke-Template":
            fps = self.get_fps()
            resolution = self.get_resolution()
            options = self.get_options()
            if self._is_error:
                return

        extension = self.extension_input.currentText()
        template = self.template_input.text()
        output_path = self.output_path.text()
        is_slate = self.slate_checkbox.isChecked()

        if engine == "Nuke-Template" and not os.path.isfile(template):
            template = os.path.join(DEFAULT_TEMPLATE_DIRECTORY, template)

        self._log_submission()

        slate_data = None
        if is_slate:
            slate_data = self.get_slate_data()

        # Create media
        if not self._is_error:
            self._create_media(
                engine,
                input_path,
                output_path,
                extension,
                resolution,
                fps,
                template,
                options,
                slate_data,
            )

        # Create tracking version
        if not self._is_error and is_tracking:
            self._create_tracking_version(version, output_path)

        logger.info("Data submitted successfully!")

    def prefill_form(self, environment):
        """
        Prefills the form fields with the provided environment instance.

        Args:
            environment (Environment): An instance of the Environment class that contains
                                        the data to prefill in the form fields.
        """
        if environment.artist_name:
            self.artist_input.setText(environment.artist_name)
        if environment.entity_name:
            self.link_input.setText(environment.entity_name)
        if environment.task_name:
            self.task_input.setText(environment.task_name)
        if environment.project_name:
            self.project_input.setText(environment.project_name)

    def update_render_settings(self):
        """
        Updates render settings based on selected preset and engine.
        """
        self._update_render_fields_visibility()

        preset = self.preset_input.currentText()
        engine = self.engine_input.currentText()

        extension = None
        if self.extension_input.count():
            extension = self.extension_input.currentText()
            self.extension_input.clear()

        items = SUPPORTED_FILE_TYPES.get(engine.lower(), [])
        if items:
            self.extension_input.addItems(items)
            if extension in items:
                self.extension_input.setCurrentText(extension)

        if preset != "None" and preset in self.presets:
            preset_info = self.presets[preset]
            self.extension_input.setCurrentText(preset_info.get("extension", ""))
            self.resolution_input.setText(preset_info.get("resolution", ""))
            self.fps_input.setText(preset_info.get("fps", ""))
            self.set_options(preset_info.get("options", {}))
            self.slate_checkbox.setChecked(preset_info.get("slate", False))
            self.engine_input.setCurrentText(preset_info.get("engine", ""))
            self.template_input.setText(preset_info.get("template", ""))

        self._set_fields_enabled(preset == "None")
