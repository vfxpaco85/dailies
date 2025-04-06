import os
import logging

from dailies.constant.main import ENV_VAR_CONFIG, LOG_FILE_PATH, LOG_FORMAT
from dailies.constant.tracking import TRACKING_ENGINE, API_URLS, TRACKING_API_TOKEN

# Set up logging
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


class Environment:
    """
    A class that encapsulates the environment configuration, loading values
    from environment variables. If some variables are missing, it attempts
    to fetch additional details (such as project or entity IDs) from the
    tracking software.

    Attributes:
        path (str): The path to the video file.
        version (str): The version name of the project.
        description (str): A description for the project or task.
        artist (str): The name of the artist associated with the project.
        link (str): A link related to the project or task.
        task (str): The task name.
        project_name (str): The name of the project.
        project_id (str or None): The project ID, or None if not provided.
        entity_name (str): The name of the entity (e.g., shot, sequence).
        entity_id (str or None): The entity ID, or None if not provided.
        entity_type (str): The type of the entity (e.g., "Shot"). Defaults to "Shot".
        artist_name (str): The name of the artist.
        artist_id (str): The ID of the artist.
        tracking_software (TrackingSoftware): An instance of the tracking software,
                                               created using the factory.
    """

    def __init__(self):
        """
        Initializes an Environment object by reading environment variables
        defined in `ENV_VAR_CONFIG`. If these variables are not available,
        it queries the tracking software for the project and entity IDs.

        The following environment variables are fetched:
            - path: Path to the file
            - version: Version name
            - description: Description of the task or project
            - artist: Name of the artist
            - link: URL related to the task or project
            - task: Task name
            - project_name: Project name
            - project_id: Optional project ID
            - entity_name: Entity name (e.g., shot, sequence)
            - entity_id: Optional entity ID
            - entity_type: Entity type, defaults to "Shot"
            - artist_name: Artist name
            - artist_id: Artist ID
        """
        # Initialize all variables from ENV_VAR_CONFIG
        self.path = os.getenv(ENV_VAR_CONFIG["path"])
        self.version = os.getenv(ENV_VAR_CONFIG["version"])
        self.description = os.getenv(ENV_VAR_CONFIG["description"])
        self.artist = os.getenv(ENV_VAR_CONFIG["artist"])
        self.link = os.getenv(ENV_VAR_CONFIG["link"])
        self.task = os.getenv(ENV_VAR_CONFIG["task"])
        self.project_name = os.getenv(ENV_VAR_CONFIG["project"])
        self.project_id = os.getenv(
            ENV_VAR_CONFIG["project_id"]
        )  # Can be None if not provided
        self.entity_name = os.getenv(ENV_VAR_CONFIG["entity_name"])
        self.entity_id = os.getenv(
            ENV_VAR_CONFIG["entity_id"]
        )  # Entity ID, can be None
        self.entity_type = os.getenv(
            ENV_VAR_CONFIG["entity_type"], "Shot"
        )  # Default to "Shot"
        self.artist_name = os.getenv(ENV_VAR_CONFIG["artist_name"])
        self.artist_id = os.getenv(ENV_VAR_CONFIG["artist_id"])
        self.tracking_software = None

    @property
    def tracking_software(self):
        if self._tracking_software is None:
            from dailies.factory import TrackingSoftwareFactory

            self._tracking_software = TrackingSoftwareFactory.get_tracking_software(
                TRACKING_ENGINE
            )
        return self._tracking_software

    @tracking_software.setter
    def tracking_software(self, tracking_software):
        """Setter for tracking_software."""
        self._tracking_software = tracking_software

    def fetch_project_id(self):
        """
        Retrieves the project ID from the tracking software if it hasn't already
        been set via the environment variable. If the `project_name` is available,
        it queries the tracking software to fetch the project ID.

        Returns:
            str or None: The project ID, or None if it could not be fetched.
        """
        if not self.project_id and self.project_name:
            self.project_id = self.tracking_software.get_project_id(self.project_name)
        return self.project_id

    def fetch_entity_id(self):
        """
        Retrieves the entity ID from the tracking software if it hasn't already
        been set via the environment variable. If the `entity_name` is available,
        it queries the tracking software to fetch the entity ID.

        Returns:
            str or None: The entity ID, or None if it could not be fetched.
        """
        if not self.entity_id and self.entity_name:
            self.entity_id = self.tracking_software.get_entity_id(self.entity_name)
        return self.entity_id

    def log_configuration(self):
        """
        Logs the current environment configuration using the logging module.
        """
        logger.info("Environment Configuration:")
        logger.info(f"Video Path: {self.path}")
        logger.info(f"Version: {self.version}")
        logger.info(f"Description: {self.description}")
        logger.info(f"Artist: {self.artist}")
        logger.info(f"Link: {self.link}")
        logger.info(f"Task: {self.task}")
        logger.info(f"Project Name: {self.project_name}")
        logger.info(f"Project ID: {self.fetch_project_id()}")
        logger.info(f"Entity Name: {self.entity_name}")
        logger.info(f"Entity ID: {self.fetch_entity_id()}")
        logger.info(f"Entity Type: {self.entity_type}")
        logger.info(f"Artist Name: {self.artist_name}")
        logger.info(f"Artist ID: {self.artist_id}")


# Main method for testing
if __name__ == "__main__":
    # Create an instance of the Environment class
    env = Environment()

    # Log the environment configuration
    env.log_configuration()
