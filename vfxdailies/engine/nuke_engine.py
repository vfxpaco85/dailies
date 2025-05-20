import logging
import os

from dailies.constant.main import (
    LOG_FORMAT,
    LOG_FILE_PATH,
    FRAME_START_NUMBER,
    FRAME_PADDING_FORMAT,
)
from dailies.constant.engine import (
    SUPPORTED_FILE_TYPES,
    FORMAT_CODECS,
    NUKE_FRAME_PADDING_FORMAT,
)
from dailies.engine.video_engine import VideoEngine
from dailies.nuke_write_config import (
    MOVConfigurator,
    EXRConfigurator,
    DNXConfigurator,
    JPEGConfigurator,
    GIFConfigurator,
    MXFConfigurator,
    PNGConfigurator,
    TargaConfigurator,
    TIFFConfigurator,
    XPMConfigurator,
    YUVConfigurator,
)

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

# Only import nuke if available
try:
    import nuke

    NukeAvailable = True
except ImportError:
    NukeAvailable = False
    logger.warning("Nuke is not available. Media creation using Nuke cannot proceed.")


def validate_file_path(file_path):
    """
    Helper function to validate input file path existence.

    Args:
        file_path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if NUKE_FRAME_PADDING_FORMAT in file_path:
        file_path = file_path.replace(NUKE_FRAME_PADDING_FORMAT, FRAME_START_NUMBER)
    if FRAME_PADDING_FORMAT in file_path:
        file_path = file_path.replace(FRAME_PADDING_FORMAT, FRAME_START_NUMBER)
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return False
    return True


class NukeEngine(VideoEngine):
    """
    Media engine implementation using Nuke's Python API for creating media files
    (video or image sequence) and optionally embedding a slate.
    """

    def create_media(
        self,
        input_path,
        output_path,
        resolution,
        extension,
        fps=None,
        options=None,
        slate_data=None,
    ):
        """
        Creates a media file (video or image sequence) using Nuke's Python API by setting up nodes
        for reading and writing.

        Args:
            input_path (str): Path to the input image sequence, video file, or media source.
            output_path (str): Path to save the output media file (video or image sequence).
            resolution (tuple): Resolution of the output media in the form (width, height).
            extension (str): Output file extension (e.g., "mov", "png", "exr").
            fps (int, optional): Frames per second for the output media (used for videos).
            options (dict, optional): Additional options for configuring the output media (e.g., encoding settings).
            slate_data (dict, optional): Data for generating a slate frame (if applicable, e.g., for videos or image sequences).
        """
        if not NukeAvailable:
            logger.error("Nuke is not available, cannot proceed with media creation.")
            return

        # Validate file paths before proceeding
        if not validate_file_path(input_path):
            return

        # Check if the file extension is supported by Nuke via FORMAT_CODECS
        if extension not in SUPPORTED_FILE_TYPES["nuke"]:
            logger.warning(
                f"File extension '{extension}' is not supported by Nuke engine. Supported types: {FORMAT_CODECS['nuke']}"
            )
            return

        try:
            # Clear any existing Nuke script
            nuke.scriptClear()

            # Create read node for the input file (image sequence or video)
            logger.info("Creating read node")
            read_node = nuke.createNode("Read")
            input_path = input_path.replace(
                FRAME_PADDING_FORMAT, NUKE_FRAME_PADDING_FORMAT
            )
            read_node["file"].setValue(input_path)
            logger.info(f"Set read node input path to {input_path}")

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

            # Create write node for the output media
            logger.info("Creating write node")
            write_node = nuke.createNode("Write")
            write_node["file"].setValue(output_path)
            write_node["file_type"].setValue(extension)
            write_node["first"].setValue(first_frame)
            write_node["last"].setValue(last_frame)

            # Dynamically select the appropriate configurator based on the extension
            write_node_configurator = None
            if extension in SUPPORTED_FILE_TYPES["nuke"] and options:
                logger.info("Setting options")

                if extension == "mov":
                    write_node_configurator = MOVConfigurator()
                elif extension == "exr":
                    write_node_configurator = EXRConfigurator()
                elif extension == "dnx":
                    write_node_configurator = DNXConfigurator()
                elif extension == "jpeg":
                    write_node_configurator = JPEGConfigurator()
                elif extension == "gif":
                    write_node_configurator = GIFConfigurator()
                elif extension == "mxf":
                    write_node_configurator = MXFConfigurator()
                elif extension == "png":
                    write_node_configurator = PNGConfigurator()
                elif extension == "targa":
                    write_node_configurator = TargaConfigurator()
                elif extension == "tiff":
                    write_node_configurator = TIFFConfigurator()
                elif extension == "xpm":
                    write_node_configurator = XPMConfigurator()
                elif extension == "yuv":
                    write_node_configurator = YUVConfigurator()

                # Apply the configuration to the write node based on the chosen file type
                if write_node_configurator:
                    write_node_configurator.configure(
                        write_node, frame_rate=fps, **options
                    )

            # Check if resizing is needed to match the target resolution
            input_resolution = read_node.width(), read_node.height()
            if input_resolution != resolution:
                logger.info("Creating resize node")
                resize_node = nuke.createNode("Resize")
                resize_node.setInput(0, read_node)
                resize_node["resize"].setValue("fit")
                resize_node["box_width"].setValue(resolution[0])
                resize_node["box_height"].setValue(resolution[1])

                write_node.setInput(0, resize_node)
            else:
                write_node.setInput(0, read_node)

            # Execute the Nuke node graph to render the media
            nuke.execute(write_node, first_frame, last_frame)
            logger.info(f"Media created successfully using Nuke at {output_path}")

        except Exception as e:
            logger.error(f"Error during media creation with Nuke: {e}")

    def _get_sequence_range(self, input_path):
        """
        Helper function to extract the frame range from the image sequence.
        Args:
            input_path (str): Path to the input image sequence.
        Returns:
            tuple: (first_frame, last_frame) if sequence is found, None otherwise.
        """
        base_path = input_path.split("###")[0]
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
    extension = (
        "mov"  # Change to the desired file extension (e.g., "mov", "png", "exr")
    )
    fps = 30  # Frames per second for the video
    resolution = (1920, 1080)  # Resolution of the output video or image sequence

    # Options for configuring the write node (if any)
    options = {"mov64_codec": "h264", "mov64_quality": "Low", "mov64_bitrate": "2000"}

    # Instantiate the NukeEngine
    engine = NukeEngine()

    # Test media creation with the provided paths and settings
    engine.create_media(input_path, output_path, fps, resolution, extension, options)


if __name__ == "__main__":
    main()
