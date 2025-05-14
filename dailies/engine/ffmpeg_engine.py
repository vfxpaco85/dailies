import os
import logging
import subprocess
from pathlib import Path

from dailies.constant.main import (
    DEFAULT_TMP_DIRECTORY,
    LOG_FORMAT,
    LOG_FILE_PATH,
    FRAME_PADDING_FORMAT,
    FRAME_START_NUMBER,
)
from dailies.constant.engine import (
    SUPPORTED_FILE_TYPES,
    FORMAT_CODECS,
    FFMPEG_FONT_SIZE,
    FFMPEG_SPACING_SIZE,
    FFMPEG_FONT_PATH,
    IMAGE_SEQUENCES_FILE_TYPES,
    VIDEO_FILE_TYPES,
)
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


def validate_file_path(file_path):
    """
    Helper function to validate the input file path existence.

    Args:
        file_path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    file_path = file_path.replace(FRAME_PADDING_FORMAT, FRAME_START_NUMBER)
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return False
    return True


class FFmpegEngine(VideoEngine):
    """
    Media engine implementation using FFmpeg for creating media files (video or image sequences).

    This class leverages FFmpeg for creating media files from image sequences or videos.
    It supports both video generation and other media types such as image sequences.
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
        Creates a media file (video or image sequence) using FFmpeg from an input source.

        Args:
            input_path (str): Path to the input image sequence, video file, or other media source.
            output_path (str): Path to save the output media file.
            resolution (tuple): Resolution of the output media in the form (width, height).
            extension (str): Output file extension (e.g., "mov", "mp4", "png", etc.).
            fps (int, optional): Frames per second for the output media (used for video files). Default is None.
            options (dict, optional): Additional options for FFmpeg, such as encoding settings or codec preferences.
            slate_data (dict, optional): Data to generate a slate (e.g., text for video frames) if applicable.
        """
        # Validate input file path
        if not validate_file_path(input_path):
            return

        # Check if the file extension is supported by FFmpeg
        if extension not in SUPPORTED_FILE_TYPES["ffmpeg"]:
            logger.error(f"Unsupported file extension for FFmpeg: {extension}")
            return

        codec = None
        pix_fmt = None

        # We don't need codec and pixel format when extracting image sequence from video
        input_file_extension = os.path.splitext(input_path)[1][1:].lower()
        if input_file_extension not in VIDEO_FILE_TYPES and extension in IMAGE_SEQUENCES_FILE_TYPES:

            # Get codec and pixel format for the given file extension
            codec, pix_fmt = FORMAT_CODECS["ffmpeg"][extension]

        # If slate data is provided, generate and add a slate frame (only for image sequences)
        slate_file = None
        if slate_data:
            # Get the file extension from the input image sequence to match the slate format
            file_extension = input_path.split(".")[-1]
            slate_file = Path(DEFAULT_TMP_DIRECTORY) / f"slate_with_text.{file_extension}" # Single image for slate
            slate_file = slate_file.as_posix()  # Ensures forward slashes
            logger.info("Generating slate file.")
            self.generate_slate_frame(slate_data, slate_file)
            logger.info(f"Slate file: {slate_file}")

        # Create the input list file (for image sequence or video)
        input_list_file_path = Path(DEFAULT_TMP_DIRECTORY) / "temp_file_list.txt"
        input_list_file_path = input_list_file_path.as_posix()  # Ensures forward slashes
        try:
            with open(input_list_file_path, "w+") as fp:
                if slate_file:
                    fp.write(f"file '{slate_file}'\n")
                # Add the input media (image sequence or video)
                fp.write(f"file '{input_path}'\n")

            ffmpeg_command = self.build_ffmpeg_command(
                input_list_file_path, resolution, codec, pix_fmt, output_path, options, fps
            )

            # Run the FFmpeg command to create the media
            logger.info(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            subprocess.run(ffmpeg_command, check=True)
            logger.info(f"Media created successfully using FFmpeg at {output_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during media creation with FFmpeg: {e}")
            logger.error(f"FFmpeg command: {' '.join(ffmpeg_command)}")
            logger.error(f"Error Output:\n{e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(f"FFmpeg command: {' '.join(ffmpeg_command)}")

    def build_ffmpeg_command(
        self, input_list_file, resolution, codec, pix_fmt, output_path, options=None, fps=None
    ):
        """
        Builds the FFmpeg command for processing media files.

        Args:
            input_list_file (str): Path to the file containing the list of input media.
            resolution (tuple): Resolution (width, height) for the output media.
            codec (str): Video codec to use for the output media.
            pix_fmt (str): Pixel format for the output media.
            output_path (str): Path where the output media will be saved.
            options (dict, optional): Additional FFmpeg options.
            fps (int, optional): Frames per second for video output (only needed for image sequences). Default is None.

        Returns:
            list: FFmpeg command as a list of arguments.
        """
        ffmpeg_command = [
            "ffmpeg",
            "-loglevel", "info",  # Add loglevel info for FFmpeg output
            "-f", "concat",  # Specify concatenation mode
            "-safe", "0",  # Allow unsafe file paths
            "-i", input_list_file,  # Use the temporary file list
            "-s", f"{resolution[0]}x{resolution[1]}",  # Resolution
            "-threads", "4",  # Tell FFmpeg to use 4 threads
        ]

        # Only add codec if it's not None
        if codec:
            ffmpeg_command.extend(["-c:v", codec])

        # Only add pix_fmt if it's not None
        if pix_fmt:
            ffmpeg_command.extend(["-pix_fmt", pix_fmt])

        # Only add fps if it's not None
        if fps:
            ffmpeg_command.append("-r")
            ffmpeg_command.append(str(fps))

        # Add any additional options from the options dictionary (if provided)
        if options:
            for key, value in options.items():
                if value is None:
                    ffmpeg_command.append(f"-{key}")
                else:
                    ffmpeg_command.append(f"-{key}")
                    ffmpeg_command.append(str(value))

        # Finally, add the output path as the last argument in the FFmpeg command
        ffmpeg_command.append(output_path)

        return ffmpeg_command

    def generate_slate_frame(self, data, output_file):
        """
        Generate a slate frame (e.g., for videos or image sequences) with all information from the UI.

        Args:
            data (dict): Data containing slate information such as text, resolution, etc.
            output_file (str): Path to save the generated slate frame image.
        """
        if not data:
            logger.warning("No slate data provided. Skipping slate frame generation.")
            return

        slate_text = generate_slate_text(data)

        # Get resolution from the slate data
        resolution = data[
            "resolution"
        ]  # Assuming resolution is a string, e.g., '480x270'

        # Split the slate text into lines for multiple drawtext filters
        lines = slate_text.split("\n")

        # Use the constants directly in the code
        font_size = FFMPEG_FONT_SIZE  # Font size for the text
        vertical_spacing = FFMPEG_SPACING_SIZE  # Vertical space between lines
        font_path = FFMPEG_FONT_PATH  # Path to the font file (adjust as needed)

        # Extract resolution width and height
        height = int(resolution[1])

        # Calculate the total height of all lines with spacing between them
        total_text_height = (
            sum(font_size + vertical_spacing for _ in lines) - vertical_spacing
        )  # Adjust for last line

        # Calculate the starting vertical position to center the text block
        start_y = (height - total_text_height) // 2 + 10

        # Sanitize each line to remove problematic characters like colons
        drawtext_filters = []
        for i, line in enumerate(lines):
            line = line.replace(
                ":", ""
            )  # Remove colons or other problematic characters
            y_offset = start_y + i * (font_size + vertical_spacing)
            drawtext_filters.append(
                f"drawtext=fontsize={font_size}:fontcolor=White:fontfile='{font_path}':text='{line}':x=(w-text_w)/2:y={y_offset}"
            )

        # Join all drawtext filters with commas for FFmpeg
        drawtext_filter_str = ", ".join(drawtext_filters)

        # Prepare the FFmpeg command with the dynamic resolution
        command = [
            "ffmpeg",
            "-f", "lavfi",  # Using FFmpeg's 'lavfi' (libavfilter) to generate a static color
            "-t", "0.001",  # Generate a single frame
            "-i", f"color=c=black:s={resolution[0]}x{resolution[1]}",  # Use resolution as passed in slate data (e.g. 480x270)
            "-vf", drawtext_filter_str,  # Apply the drawtext filter with multiple lines of text
            "-frames:v", "1",  # Specify that we want to generate only a single frame
            "-update", "1",
            "-y",
            output_file,  # Output the slate frame to a file
        ]

        try:
            logger.info(f"Running FFmpeg command: {' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg output:\n{result.stdout}")
            logger.error(f"FFmpeg error:\n{result.stderr}")  # Capture and log stderr
            logger.info(
                f"Slate frame created successfully using FFmpeg at {output_file}"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during media creation with FFmpeg: {e}")
            logger.error(f"FFmpeg command: {' '.join(command)}")
            logger.error(f"Error Output:\n{e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(f"FFmpeg command: {' '.join(command)}")


def main():
    # Example test paths (replace these with actual paths)
    input_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-%03d.jpg"  # Replace with a valid input media path
    output_path = "C:/Users/info/Downloads/ezgif-split/output.mov"  # Replace with a desired output path
    extension = "mov"  # Change to the desired file extension (e.g., "mov", "png", "exr")
    resolution = (1920, 1080)  # Resolution of the output video or image sequence
    fps = 30  # Frames per second for the video

    # Options for configuring the output (if any)
    options = {
        "y": None,  # Overwrite
    }

    # Slate data dictionary
    slate_data = {
        "version": "ezgif-frame-v001",
        "file": "ezgif-frame-001",
        "description": "test",
        "artist": "paco",
        "link": "seq01_shot01",
        "task": "pipe",
        "project": "foobar",
        "tracking": False,
        "resolution": "1920x1080",  # Slate resolution (make sure this matches the output resolution)
    }

    # Instantiate the FFmpegEngine
    engine = FFmpegEngine()

    # Test media creation with the provided paths and settings
    engine.create_media(
        input_path, output_path, resolution, extension, fps, options, slate_data
    )


if __name__ == "__main__":
    main()
