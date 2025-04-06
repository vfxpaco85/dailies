import logging
from abc import ABC, abstractmethod

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.constant.tracking import (
    API_URLS,
    TRACKING_ENGINE,
    TRACKING_API_TOKEN,
    TRACKING_LOGIN_USER,
)
from dailies.environment import Environment

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,  # Set the default logger level to INFO
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        LOG_FILE_PATH,
    ],
)

# Check the validity of TRACKING_ENGINE
if not TRACKING_ENGINE or TRACKING_ENGINE not in API_URLS:
    logging.error(
        f"Invalid TRACKING_ENGINE specified: {TRACKING_ENGINE}. Please check the configuration."
    )
    exit(1)

# Log warnings if credentials are missing or using default values
if not TRACKING_LOGIN_USER or TRACKING_LOGIN_USER == "USR":
    logging.error(
        "Tracking username is missing or invalid. Please set 'TRACKING_LOGIN_USER' in the environment variables."
    )

if not TRACKING_API_TOKEN or TRACKING_API_TOKEN == "PWD":
    logging.error(
        "Tracking API token is missing or invalid. Please set 'TRACKING_API_TOKEN' in the environment variables."
    )

# Log the chosen tracking engine and its corresponding API URL
logger.info(f"Using tracking engine: {TRACKING_ENGINE}")
logger.info(f"API URL for {TRACKING_ENGINE}: {API_URLS[TRACKING_ENGINE]}")


# Base class for tracking software systems like Shotgun, Ftrack, Kitsu, and Flow.
class TrackingSoftware(ABC):
    """
    Base class for tracking software systems like Shotgun, Ftrack, Kitsu, and Flow.
    Provides common methods for interacting with various tracking systems.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the TrackingSoftware instance with the given environment.

        :param environment: The environment instance that contains project and entity details.
        """
        self.environment = environment
        self.api_url = API_URLS.get(TRACKING_ENGINE)
        self.api_token = TRACKING_API_TOKEN
        self.project_id = self.environment.fetch_project_id()
        self.entity_name = self.environment.entity_name
        self.entity_id = self.environment.fetch_entity_id()
        self.entity_type = self.environment.entity_type

    def _get_headers(self):
        """
        Returns the headers required for API requests.

        :return: A dictionary containing the Authorization and Content-Type headers.
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    @abstractmethod
    def insert_version(self, version_number, video_path):
        """
        Inserts a version into the tracking system.

        :param version_number: The version number to be created.
        :param video_path: The path to the video file to be uploaded.
        """
        pass

    @abstractmethod
    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        pass

    @abstractmethod
    def get_entity_id(self, entity_name, entity_type=None):
        """
        Retrieves the entity ID based on the entity name from the tracking system.

        :param entity_name: The entity name to search for.
        :param entity_type: The entity type to use (defaults to the one in the environment).
        :return: The entity ID, or None if not found.
        """
        pass
