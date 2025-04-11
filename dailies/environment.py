import os
import logging

from dailies.constant.main import ENV_VAR_CONFIG, LOG_FILE_PATH, LOG_FORMAT
from dailies.constant.tracking import TRACKING_ENGINE

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
    from environment variables or optional constructor arguments.

    Attributes:
        project_name (str): The name of the project.
        entity_name (str): The name of the entity (e.g., shot, sequence).
        task_name (str): The name of the task (e.g., "Modeling", "Animation").
        artist_name (str): The name of the artist associated with the task.
        project_id (str or None): The project ID, or None if not provided.
        entity_id (str or None): The entity ID, or None if not provided.
        entity_type (str): The type of the entity (e.g., "Shot"). Defaults to "Shot".
        task_id (str or None): The task ID, or None if not provided.
        artist_id (str or None): The artist ID, or None if not provided.
        _tracking_software (TrackingSoftware or None): An instance of the tracking software,
                                                      created using the factory when needed.
    """

    def __init__(
        self,
        project_name: str = None,
        entity_name: str = None,
        task_name: str = None,
        artist_name: str = None,
    ):
        """
        Initializes an Environment object by reading environment variables
        defined in `ENV_VAR_CONFIG`, or using optional constructor arguments.

        :param project_name: Optional project name to override environment variable.
        :param entity_name: Optional entity name to override environment variable.
        :param task_name: Optional task name to override environment variable.
        :param artist_name: Optional artist name to override environment variable.
        """
        # Initialize all variables from ENV_VAR_CONFIG
        # Allow constructor overrides for project/entity/task/artist name
        self.project_name = project_name or os.getenv(ENV_VAR_CONFIG["project"])
        self.entity_name = entity_name or os.getenv(ENV_VAR_CONFIG["entity_name"])
        self.task_name = task_name or os.getenv(ENV_VAR_CONFIG["task_name"])
        self.artist_name = artist_name or os.getenv(ENV_VAR_CONFIG["artist_name"])

        self.project_id = os.getenv(ENV_VAR_CONFIG["project_id"])
        self.entity_id = os.getenv(ENV_VAR_CONFIG["entity_id"])
        self.entity_type = os.getenv(
            ENV_VAR_CONFIG["entity_type"], "Shot"
        )  # Default to Shot
        self.task_id = os.getenv(ENV_VAR_CONFIG["task_id"])
        self.artist_id = os.getenv(ENV_VAR_CONFIG["artist_id"])

        # Set to None because the tracking_software is lazily initialized.
        self._tracking_software = None

        # Auto-fetch IDs if not set
        if not self.project_id and self.project_name:
            self.project_id = self.fetch_project_id()
            if not self.tracking_software.project_id:
                self.tracking_software.project_id = self.project_id
        if not self.entity_id and self.entity_name and self.entity_type:
            self.entity_id = self.fetch_entity_id()
            if not self.tracking_software.entity_id:
                self.tracking_software.entity_id = self.project_id
        if not self.task_id and self.entity_name:
            self.task_id = self.fetch_task_id()
            if not self.tracking_software.task_id:
                self.tracking_software.task_id = self.task_id
        if not self.artist_id and self.artist_name:
            self.artist_id = self.fetch_artist_id()
            if not self.tracking_software.artist_id:
                self.tracking_software.artist_id = self.artist_id

    @property
    def tracking_software(self):
        """
        Retrieves the tracking software instance, creating it if necessary
        by using the factory defined in `dailies.factory.TrackingSoftwareFactory`.

        :return: An instance of the tracking software.
        """
        if self._tracking_software is None:
            from dailies.factory import TrackingSoftwareFactory

            self._tracking_software = TrackingSoftwareFactory.get_tracking_software(
                TRACKING_ENGINE
            )
        return self._tracking_software

    @tracking_software.setter
    def tracking_software(self, tracking_software):
        """
        Setter for the tracking software instance.

        :param tracking_software: The tracking software instance to set.
        """
        self._tracking_software = tracking_software

    def fetch_project_id(self):
        """
        Retrieves the project ID from the tracking software if it is not already set.
        The ID is fetched by the project name if necessary.

        :return: The project ID, or None if not available.
        """
        if not self.project_id and self.project_name:
            self.project_id = self.tracking_software.get_project_id(self.project_name)
        return self.project_id

    def fetch_entity_id(self):
        """
        Retrieves the entity ID (e.g., for a shot, asset, or sequence) from the tracking software
        if it is not already set. The ID is fetched based on the entity name and type if necessary.

        :return: The entity ID, or None if not available.
        """
        if not self.entity_id and self.entity_name and self.entity_type:
            self.entity_id = self.tracking_software.get_entity_id(
                self.entity_name, self.entity_type
            )
        return self.entity_id

    def fetch_task_id(self):
        """
        Retrieves the task ID based on the task name and project ID from the tracking software.
        The ID is fetched if it is not already set.

        :return: The task ID, or None if not available.
        """
        if not self.task_id and self.project_id and self.task_name:
            self.task_id = self.tracking_software.get_task_id(
                self.entity_id, self.task_name
            )
        return self.task_id

    def fetch_artist_id(self):
        """
        Retrieves the artist ID based on the artist name from the tracking software.
        The ID is fetched if it is not already set.

        :return: The artist ID, or None if not available.
        """
        if not self.artist_id and self.artist_name:
            self.artist_id = self.tracking_software.get_artist_id(self.artist_name)
        return self.artist_id

    def log_configuration(self):
        """
        Logs the current environment configuration using the logging module.
        This includes all project, entity, task, and artist information.

        Logs the following:
            - Project Name and ID
            - Entity Name and ID
            - Entity Type
            - Task Name and ID
            - Artist Name and ID
        """
        logger.info("Environment Configuration:")
        logger.info(f"Project Name: {self.project_name}")
        logger.info(f"Project ID: {self.fetch_project_id()}")
        logger.info(f"Entity Name: {self.entity_name}")
        logger.info(f"Entity ID: {self.fetch_entity_id()}")
        logger.info(f"Entity Type: {self.entity_type}")
        logger.info(f"Task Name: {self.task_name}")
        logger.info(f"Task ID: {self.fetch_task_id()}")
        logger.info(f"Artist Name: {self.artist_name}")
        logger.info(f"Artist ID: {self.fetch_artist_id()}")


# Main method for testing
if __name__ == "__main__":
    # Create an instance of the Environment class with optional overrides
    env = Environment(
        project_name="pipeline_test",
        entity_name="MR_LGP_01_0320",
        task_name="fx",
        artist_name="User",
    )

    # Log the environment configuration
    env.log_configuration()
