import os
import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH, FRAME_PADDING_FORMAT
from dailies.constant.engine import (
    NUKE_READ_NODE,
    NUKE_WRITE_NODE,
    NUKE_FRAME_PADDING_FORMAT,
)

# Set up logger
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

# Only import nuke if available
try:
    import nuke

    NukeAvailable = True
except ImportError:
    NukeAvailable = False
    logger.warning("Nuke is not available. Media creation using Nuke cannot proceed.")


def validate_file_path(file_path):
    """
    Helper function to validate file path existence.

    Args:
        file_path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    return True


class NukeTemplateEngine:
    """
    Media engine implementation that handles media creation using a Nuke template.

    This class applies a Nuke template to an image sequence or media file (video/image sequence)
    and renders the resulting media by executing a Nuke script.

    NUKE_READ_NODE and NUKE_WRITE_NODE are the expected node names within the Nuke template.
    These node names are deterministic and must exist in the template.
    """

    def create_media(self, input_path, output_path, template_path):
        """
        Applies a Nuke template to an image sequence or media file (video or image sequence) and
        renders the resulting media.

        Args:
            input_path (str): Path to the input image sequence or media file (video or image sequence).
            output_path (str): Path to save the rendered output media (video or image sequence).
            template_path (str): Path to the Nuke template to be used for rendering the media.

        Logs:
            Errors if the template file, Read1 node, or Write1 node are not found.
            Success or failure during the media creation process.
        """
        # Check if Nuke is available
        if not NukeAvailable:
            logger.error("Nuke is not available in this environment!")
            return

        # Check if the template file exists
        if not validate_file_path(template_path):
            return

        # Ensure the file is a valid Nuke script (.nk)
        if not template_path.lower().endswith(".nk"):
            logger.error(
                f"Invalid template file: '{template_path}' is not a valid Nuke script (.nk)."
            )
            return

        logger.info(f"Opening Nuke template: {template_path}")

        try:
            # Open the Nuke template (this will only open the template, no further operations)
            self._open_template(template_path)

            # Proceed with setting up and rendering the media
            self._setup_and_render(input_path, output_path)

        except Exception as e:
            logger.error(f"Error during media creation with template: {e}")

    def _open_template(self, template_path):
        """
        Opens a Nuke template script without performing any operations like setting input/output paths.

        Args:
            template_path (str): Path to the Nuke template to be opened.
        """
        os.environ["NUKE_NO_UPGRADE"] = "1"
        try:
            logger.info(f"Opening Nuke template: {template_path}")
            nuke.scriptOpen(template_path)
            logger.info("Template opened successfully.")
        except Exception as e:
            logger.error(f"Failed to open Nuke template: {e}")
            raise  # Reraise the exception to stop further execution if template fails to open

    def _setup_and_render(self, input_path, output_path):
        """
        Sets up the nodes and renders the media using Nuke.

        Args:
            input_path (str): Path to the input media file (image sequence/video).
            output_path (str): Path to save the output media file.
        """
        try:
            # Locate the Read node (input media)
            read_node = nuke.toNode(NUKE_READ_NODE)
            if not read_node:
                logger.error(f"{NUKE_READ_NODE} node not found in the Nuke template!")
                return

            read_node["file"].setValue(input_path)

            # Manually check the sequence range
            # Get the first and last frame from the file sequence
            frame_range = self._get_sequence_range(input_path)
            if not frame_range:
                logger.error(f"Failed to detect frame range for sequence: {input_path}")
                return

            first_frame, last_frame = frame_range
            logger.info(f"Detected frame range: {first_frame} to {last_frame}")

            # Set the first and last frames in the Read node
            read_node["first"].setValue(first_frame)
            read_node["last"].setValue(last_frame)

            # Locate the Write node (output media)
            write_node = nuke.toNode(NUKE_WRITE_NODE)
            if not write_node:
                logger.error(f"{NUKE_WRITE_NODE} node not found in the Nuke template!")
                return
            write_node["file"].setValue(output_path)

            # Execute the render process in Nuke
            nuke.execute(write_node, first_frame, last_frame)
            logger.info(f"Media created successfully with template at {output_path}")

        except Exception as e:
            logger.error(f"Error during media creation with template: {e}")

    def _get_sequence_range(self, input_path):
        """
        Helper function to extract the frame range from the image sequence.
        Args:
            input_path (str): Path to the input image sequence.
        Returns:
            tuple: (first_frame, last_frame) if sequence is found, None otherwise.
        """
        if NUKE_FRAME_PADDING_FORMAT in input_path:
            base_path = input_path.split(NUKE_FRAME_PADDING_FORMAT)[0]
        if FRAME_PADDING_FORMAT in input_path:
            base_path = input_path.split(FRAME_PADDING_FORMAT)[0]

        first_frame = None
        last_frame = None

        # Check for the first frame (assumes the first frame is 001)
        for i in range(1, 1000):  # Assuming there are fewer than 1000 frames
            file_path = (
                base_path + str(i).zfill(3) + ".jpg"
            )  # Adjust for your file extension
            if os.path.exists(file_path):
                if first_frame is None:
                    first_frame = i
            else:
                if first_frame is not None:
                    last_frame = i - 1
                    break

        return (first_frame, last_frame)


def main():
    # Example test paths (replace these with actual paths)
    input_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-###.jpg"  # Replace with a valid input media path
    output_path = "C:/Users/info/Downloads/ezgif-split/output.mov"  # Replace with a desired output path
    template_path = "C:/code/python/vfx/dailies/template/foobar.nk"  # Replace with the path to your Nuke template

    # Instantiate the NukeTemplateEngine
    engine = NukeTemplateEngine()

    # Test media creation with the provided paths
    engine.create_media(input_path, output_path, template_path)


if __name__ == "__main__":
    main()
