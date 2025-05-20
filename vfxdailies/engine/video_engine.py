from abc import ABC, abstractmethod

from dailies.constant.main import DEFAULT_SLATE_TEMPLATE


def generate_slate_text(data, template=DEFAULT_SLATE_TEMPLATE):
    """
    Generates a formatted string containing slate text using the provided data and template.

    Args:
        data (dict): Dictionary containing slate information such as path, version, description, artist, etc.
        template (str): The format template for the slate text.

    Returns:
        str: A formatted string representing the slate text with relevant information.
    """
    return template.format(
        file=data.get("file", ""),
        version=data.get("version", ""),
        description=data.get("description", ""),
        artist=data.get("artist", ""),
        link=data.get("link", ""),
        task=data.get("task", ""),
        project=data.get("project", ""),
        resolution=data.get("resolution", ""),
        fps=data.get("fps", ""),
    )


class VideoEngine(ABC):
    """
    Abstract base class for media engines, defining the interface for creating media files
    from various input formats, such as image sequences, videos, or other media types.

    This class should be inherited by specific media engine implementations, such as RVIO, FFmpeg, or Nuke.
    """

    @abstractmethod
    def create_media(
        self,
        input_path,
        output_path,
        resolution=(1920, 1080),
        extension="mov",
        fps=30,
        options=None,
        slate_data=None,
    ):
        """
        Abstract method for creating a media file (video or image sequence) from an input source.

        Args:
            input_path (str): Path to the input media (image sequence, video file, etc.).
            output_path (str): Path to save the output media file.
            fps (int, optional): Frames per second for the output media (relevant for videos). Defaults to 30.
            resolution (tuple, optional): Resolution of the output media in the form (width, height). Defaults to (1920, 1080).
            extension (str, optional): File extension for the output media (e.g., "mov", "mp4", "png"). Defaults to "mov".
            options (dict, optional): Additional options for media creation (e.g., compression, format-specific settings).
            slate_data (dict, optional): Data for generating a slate (if applicable). This is relevant for media formats like video.
        """
        pass
