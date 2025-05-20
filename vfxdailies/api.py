import json
import logging
from constant import LOG_FORMAT, LOG_FILE_PATH
from factory import TrackingSoftwareFactory, VideoEngineFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler(LOG_FILE_PATH),  # Log to a file for persistence
    ],
)


# Function to create media (video or image sequence) with tracking flag
def create_media_with_tracking(
    engine_type: str,
    input_path: str,
    output_path: str,
    frame_rate: int = 30,
    tracking_software: str = None,
    project_id: int = None,
    version_number: int = None,
    slate_data: dict = None,
    template_name: str = None  # Only used for Nuke-Template
):
    """
    Create media (video/image sequence) from the provided input path using the specified engine.
    Optionally, add slate data and handle tracking. Handles Nuke-Template engine with template_name.
    """
    try:
        # Create video engine using the VideoEngineFactory
        video_engine = VideoEngineFactory.get_video_engine(engine_type)

        # Handle NukeTemplate (which requires template_name)
        if engine_type == "nuke-template" and template_name:
            video_engine.create_media(input_path, output_path, template_name)
        else:
            # If slate data is provided, handle it for applicable engines (ffmpeg, nuke, rvio)
            if slate_data and engine_type in ["ffmpeg", "nuke", "rvio"]:
                video_engine.create_media_with_slate(input_path, output_path, frame_rate, slate_data)
            else:
                video_engine.create_media(input_path, output_path, frame_rate)

        logging.info(f"Media created successfully at {output_path} using {engine_type} engine.")

        # If tracking is required, insert the version into the specified tracking software
        if tracking_software and project_id and version_number:
            insert_version_into_tracking(
                tracking_software, project_id, version_number, output_path
            )
            logging.info(f"Version {version_number} inserted into {tracking_software}.")

    except Exception as e:
        logging.error(f"Error creating media with tracking: {e}")
        raise


# Function to create media without tracking flag
def create_media_without_tracking(
    engine_type: str,
    input_path: str,
    output_path: str,
    frame_rate: int = 30,
    slate_data: dict = None,
    template_name: str = None  # Only used for Nuke-Template
):
    """
    Create media (video/image sequence) without tracking.
    Handles Nuke-Template engine with template_name.
    """
    try:
        # Create video engine using the VideoEngineFactory
        video_engine = VideoEngineFactory.get_video_engine(engine_type)

        # Handle NukeTemplate (which requires template_name)
        if engine_type == "nuke-template" and template_name:
            video_engine.create_media(input_path, output_path, template_name)
        else:
            # If slate data is provided, handle it for applicable engines (ffmpeg, nuke, rvio)
            if slate_data and engine_type in ["ffmpeg", "nuke", "rvio"]:
                video_engine.create_media_with_slate(input_path, output_path, frame_rate, slate_data)
            else:
                video_engine.create_media(input_path, output_path, frame_rate)

        logging.info(f"Media created successfully at {output_path} using {engine_type} engine.")

    except Exception as e:
        logging.error(f"Error creating media without tracking: {e}")
        raise


# Function to insert version into tracking software
def insert_version_into_tracking(
    tracking_software_type: str, project_id: int, version_number: int, video_path: str
):
    try:
        # Get tracking software instance from factory
        tracking_software = TrackingSoftwareFactory.get_tracking_software(
            tracking_software_type
        )

        logging.info(
            f"Inserting version {version_number} into {tracking_software_type}."
        )
        # Insert version into tracking software
        tracking_software.insert_version(version_number, video_path)

        logging.info(
            f"Version {version_number} inserted into {tracking_software_type}."
        )
    except Exception as e:
        logging.error(f"Error inserting version into tracking: {e}")
        raise


# Function to handle slate data (provided as JSON or key-value pairs)
def handle_slate_data(slate_data: str):
    """
    Parse slate data provided either as a JSON string or as key-value pairs.
    """
    try:
        if slate_data:
            try:
                # Attempt to parse slate data as JSON
                slate_data = json.loads(slate_data)
                logging.info(f"Slate data parsed as JSON: {slate_data}")
            except json.JSONDecodeError:
                # If JSON fails, treat as key-value pair string (e.g., artist=John, project=Test)
                slate_data = dict(
                    (key.strip(), value.strip())
                    for key, value in (
                        item.split("=") for item in slate_data.split(",")
                    )
                )
                logging.info(f"Slate data parsed as key-value pairs: {slate_data}")

            return slate_data
        else:
            return {}

    except Exception as e:
        logging.error(f"Error parsing slate data: {e}")
        raise


# Function to handle slate creation specifically for engines that support it (ffmpeg, nuke, rvio)
def create_media_with_slate(
    engine_type: str,
    input_path: str,
    output_path: str,
    frame_rate: int,
    slate_data: dict
):
    """
    Create media with a slate (title card, artist info, etc.) for supported engines.
    """
    try:
        # Ensure the slate functionality is only enabled for ffmpeg, nuke, and rvio
        if engine_type not in ["ffmpeg", "nuke", "rvio"]:
            raise ValueError(
                f"Slate creation is not supported for {engine_type} engine."
            )

        video_engine = VideoEngineFactory.get_video_engine(engine_type)
        logging.info(f"Creating media with slate using {engine_type} engine.")
        video_engine.create_media_with_slate(
            input_path, output_path, frame_rate, slate_data
        )

    except Exception as e:
        logging.error(f"Error creating media with slate: {e}")
        raise
