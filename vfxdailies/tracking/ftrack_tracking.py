import logging
from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.environment import Environment
from dailies.tracking.tracking import TrackingSoftware

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

# Try importing ftrack_api and set availability flag
try:
    import ftrack_api

    FTRACK_API_AVAILABLE = True
except ImportError as e:
    FTRACK_API_AVAILABLE = False
    logging.error(f"Failed to import ftrack_api module: {e}")


class FtrackTracking(TrackingSoftware):
    """
    Ftrack-specific implementation of the TrackingSoftware class.
    Handles interactions with Ftrack's API.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the FtrackTracking instance.

        :param environment: The environment instance that contains project and entity details.
        """
        super().__init__(environment)

        # Initialize the session property if Ftrack API is available
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            self.session = None
        else:
            self.session = ftrack_api.Session()

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Ftrack.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            return None

        try:
            if not self.session:
                logging.error("Ftrack API session is not available.")
                return None

            project = self.session.query(
                f"select * from Project where name='{project_name}'"
            ).one()
            return project["id"] if project else None
        except Exception as e:
            logging.error(f"Error fetching project ID from Ftrack: {e}")
            return None

    def get_entity_id(self, entity_name, entity_type=None):
        """
        Retrieves the entity ID based on the entity name and entity type from Ftrack.

        :param entity_name: The entity name to search for.
        :param entity_type: The entity type to use (defaults to the one in the environment).
        :return: The entity ID, or None if not found.
        """
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            return None

        try:
            if not self.session:
                logging.error("Ftrack API session is not available.")
                return None

            entity_type = entity_type or self.entity_type
            entity = self.session.query(
                f"select * from {entity_type} where name='{entity_name}'"
            ).one()
            return entity["id"] if entity else None
        except Exception as e:
            logging.error(f"Error fetching entity ID from Ftrack: {e}")
            return None

    def get_task_id(self, entity_id, task_name):
        """
        Retrieves the task ID based on the entity ID and task name from Ftrack.

        :param entity_id: The entity ID (e.g., shot, asset).
        :param task_name: The task name (e.g., "Animation", "Lighting").
        :return: The task ID, or None if not found.
        """
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            return None

        try:
            if not self.session:
                logging.error("Ftrack API session is not available.")
                return None

            task = self.session.query(
                f"select * from Task where entity_id={entity_id} and name='{task_name}'"
            ).one()
            return task["id"] if task else None
        except Exception as e:
            logging.error(f"Error fetching task ID from Ftrack: {e}")
            return None

    def get_artist_id(self, artist_name):
        """
        Retrieves the artist ID based on the artist's name from Ftrack.

        :param artist_name: The name of the artist.
        :return: The artist ID, or None if not found.
        """
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            return None

        try:
            if not self.session:
                logging.error("Ftrack API session is not available.")
                return None

            artist = self.session.query(
                f"select * from HumanUser where name='{artist_name}'"
            ).one()
            return artist["id"] if artist else None
        except Exception as e:
            logging.error(f"Error fetching artist ID from Ftrack: {e}")
            return None

    def insert_version(self, version_name, video_path, comment):
        """
        Inserts a version into Ftrack.

        :param version_name: The version name to be created (e.g., "v001", "v002", etc.).
        :param video_path: The path to the video file to be uploaded.
        :param comment: A comment describing the version.
        """
        if not FTRACK_API_AVAILABLE:
            logging.error("Ftrack API is not available.")
            return None

        try:
            if not self.session:
                logging.error("Ftrack API session is not available.")
                return None

            project = self.session.query(
                f"select * from Project where id={self.project_id}"
            ).one()

            version = ftrack_api.Entity("Version")
            version["name"] = version_name  # Update to version_name
            version["project"] = project
            version["file"] = video_path

            self.session.add(version)
            self.session.commit()
            logging.info(f"Version '{version_name}' inserted into Ftrack.")

            # Add comment
            comment_entity = ftrack_api.Entity("Note")
            comment_entity["content"] = comment
            comment_entity["project"] = project
            comment_entity["entity"] = version
            self.session.add(comment_entity)
            self.session.commit()
            logging.info(f"Added comment: '{comment}'")

        except Exception as e:
            logging.error(f"Error inserting version into Ftrack: {e}")


def main():
    """
    Main function to test the FtrackTracking class.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Assume we have an environment object
    environment = Environment(project_name="pipeline_test")

    # Create a FtrackTracking instance
    ftrack_tracker = FtrackTracking(environment)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = ftrack_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = ftrack_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")

    # Test fetching artist ID by name
    artist_name = "John Doe"  # Replace with an actual artist name
    artist_id = ftrack_tracker.get_artist_id(artist_name)
    logging.info(f"Artist ID for '{artist_name}': {artist_id}")

    # Test inserting a version
    version_name = "v001"
    video_path = "/path/to/video/file.mov"  # Replace with an actual video file path
    comment = "Initial version"
    ftrack_tracker.insert_version(version_name, video_path, comment)


if __name__ == "__main__":
    main()
