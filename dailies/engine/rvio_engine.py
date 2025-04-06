import logging
import os
import subprocess

from dailies.constant.main import DEFAULT_TMP_DIRECTORY, LOG_FORMAT, LOG_FILE_PATH
from dailies.constant.engine import SUPPORTED_FILE_TYPES, FORMAT_CODECS
from dailies.engine.video_engine import VideoEngine, generate_slate_text

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

# Attempt to import RVIO (rv). If not available, log a warning.
try:
    import rv  # Assuming `rv` is the RVIO library you are using

    RVIOAvailable = True
except ImportError:
    rv = None
    RVIOAvailable = False
    logger.warning(
        "RVIO (rv) library not found. Slate frame generation and overlay will be skipped."
    )


def validate_file_path(file_path):
    """
    Helper function to validate the input file path existence.

    Args:
        file_path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return False
    return True


class RVIOEngine(VideoEngine):
    """
    Media engine implementation using RVIO for creating media files (video, image sequences) and slate generation.

    This class leverages RVIO for creating media files (videos or image sequences) from input sources,
    and it supports the generation and overlay of slate frames onto media.
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
        Creates a media file (video or image sequence) from input using RVIO.

        Args:
            input_path (str): Path to the input image sequence, video file, or other media source.
            output_path (str): Path to save the output media file.
            resolution (tuple): Resolution of the output media in the form (width, height).
            extension (str): Output file extension (e.g., "mov", "mp4", "png", etc.).
            fps (int, optional): Frames per second for the output media (used for videos).
            options (dict, optional): Additional options such as encoding or compression settings.
            slate_data (dict, optional): Data for generating a slate frame (if applicable).
        """
        # Validate input file path
        if not validate_file_path(input_path):
            return

        if not RVIOAvailable:
            logger.error("RVIO is not available, cannot proceed with media creation.")
            return

        if extension not in SUPPORTED_FILE_TYPES["rvio"]:
            logger.error(f"Unsupported file extension for RVIO: {extension}")
            return

        # Get codec for the given file extension
        codec = FORMAT_CODECS["rvio"][extension]

        # Generate the slate frame if slate data is provided
        slate_file = None
        if slate_data:
            slate_file = self.generate_slate_frame(slate_data, resolution, extension)
            if not slate_file:
                logger.error("Failed to generate slate frame. Aborting media creation.")
                return

        # Handle the media creation based on the input (video or image sequence)
        rvio_command = [
            "rvio",
            "--input",
            os.path.join(input_path),
            "--output",
            output_path,
            "--codec",
            codec,
            "--fps",
            str(fps),
            "--resolution",
            f"{resolution[0]}x{resolution[1]}",
        ]

        # Add any additional options to the RVIO command
        if options:
            for key, value in options.items():
                rvio_command.append(f"--{key}")
                if value is not None:
                    rvio_command.append(str(value))

        # Run the RVIO command to create the media file
        try:
            subprocess.run(rvio_command, check=True)
            logger.info(f"Media created successfully using RVIO at {output_path}")

            # If slate was generated, overlay it on the media
            if slate_file:
                self.add_slate_to_media(slate_file, output_path, output_path)
                # Clean up slate file after adding it
                if os.path.exists(slate_file):
                    os.remove(slate_file)
                    logger.info(f"Slate file {slate_file} has been deleted.")
            else:
                logger.info("No slate to add, media created successfully.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during media creation with RVIO: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def generate_slate_frame(self, data, resolution, extension):
        """
        Generate a slate frame (e.g., for videos or image sequences) based on the provided data.
        The slate will always be a single frame.

        Args:
            data (dict): Data for creating the slate (e.g., text, color, resolution, position).
            resolution (tuple): The resolution to generate the slate at (width, height).
            extension (str): The desired output extension (e.g., "exr", "png", "jpg").
        """
        if not RVIOAvailable:
            logger.warning("RVIO is not available. Skipping slate frame creation.")
            return None

        width, height = resolution
        slate_format = (
            extension.lower() if extension in ["jpg", "png", "exr"] else "exr"
        )  # Default to EXR for unrecognized formats

        try:
            slate_file = os.path.join(
                DEFAULT_TMP_DIRECTORY, f"generated_slate.{slate_format}"
            )
            slate_image = rv.createImage(
                width, height, rv.Color(0, 0, 0)
            )  # Create black image of the desired size
            slate_text = generate_slate_text(
                data
            )  # Use the generate_slate_text from video_engine
            slate_image.addText(
                slate_text,
                position=(width / 4, height / 4),
                font_size=50,
                color=(1, 1, 1),
            )  # Add white text
            slate_image.write(slate_file)
            logger.info(f"Slate frame saved to {slate_file}")
            return slate_file
        except Exception as e:
            logger.error(f"Error creating slate frame: {e}")
            return None

    def add_slate_to_media(self, slate_file, media_file, output_file):
        """
        Add a slate (e.g., for videos or image sequences) to a media file.
        The slate is always applied as a single frame at the beginning.

        Args:
            slate_file (str): Path to the slate frame image.
            media_file (str): Path to the input media file (video or image sequence).
            output_file (str): Path to save the output media with slate added.
        """
        if not RVIOAvailable:
            logger.warning("RVIO is not available. Skipping slate addition to media.")
            return

        try:
            media = rv.loadFile(media_file)  # Load the media file
            slate = rv.loadFile(slate_file)  # Load the slate image

            if media.type() == "video":
                # If the media is a video, we add the slate as the first frame
                media.addFrames(
                    slate, position=0
                )  # Insert slate at the beginning of the video
                media.write(output_file)  # Write the modified video to the output file
            else:
                # For image sequences, we need to prepend the slate frame
                media.addFrames(
                    slate, position=0
                )  # Insert slate as the first frame in the sequence
                media.write(
                    output_file
                )  # Write the modified image sequence to the output file

            logger.info(f"Media with slate saved to {output_file}")
        except Exception as e:
            logger.error(f"Error adding slate to media: {e}")


def main():
    # Example test paths (replace these with actual paths)
    input_path = "path/to/your/input_media.mov"  # Replace with a valid input media path
    output_path = "path/to/your/output_media.mov"  # Replace with a desired output path
    extension = (
        "mov"  # Change to the desired file extension (e.g., "exr", "png", "jpg")
    )
    fps = 24  # Frames per second for the video
    resolution = (1920, 1080)  # Resolution of the output video or image sequence

    # Options for configuring the output (if any)
    options = {"compression": "medium"}  # Example compression options

    # Instantiate the RVIOEngine
    engine = RVIOEngine()

    # Test media creation with the provided paths and settings
    engine.create_media(input_path, output_path, fps, resolution, extension, options)


if __name__ == "__main__":
    main()
