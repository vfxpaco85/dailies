import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.constant.tracking import TRACKING_LOGIN_USR
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

# Try importing shotgun_api3 and set availability flag
try:
    import shotgun_api3

    SHOTGUN_API_AVAILABLE = True
except ImportError as e:
    SHOTGUN_API_AVAILABLE = False
    logging.error(f"Failed to import shotgun_api3 module: {e}")


class ShotgunTracking(TrackingSoftware):
    """
    Shotgun-specific implementation of the TrackingSoftware class.
    Handles interactions with Shotgun's API.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the ShotgunTracking instance.

        :param environment: The environment instance that contains project and entity details.
        """
        super().__init__(environment)

        # Initialize the session property if Shotgun API is available
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            self.sg = None
            return None
        else:
            self.sg = shotgun_api3.Shotgun(
                self.api_url, login=TRACKING_LOGIN_USR, password=self.api_token
            )

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Shotgun.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            return None

        try:
            if not self.sg:
                logging.error("Shotgun API session is not available.")
                return None

            project = self.sg.find_one("Project", [["name", "is", project_name]])
            return project["id"] if project else None
        except Exception as e:
            logging.error(f"Error fetching project ID from Shotgun: {e}")
            return None

    def get_entity_id(self, entity_name, entity_type=None):
        """
        Retrieves the entity ID based on the entity name and entity type from Shotgun.

        :param entity_name: The entity name to search for.
        :param entity_type: The entity type to use (defaults to the one in the environment).
        :return: The entity ID, or None if not found.
        """
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            return None

        try:
            if not self.sg:
                logging.error("Shotgun API session is not available.")
                return None

            entity_type = entity_type or self.entity_type
            entity = self.sg.find_one(entity_type, [["code", "is", entity_name]])
            return entity["id"] if entity else None
        except Exception as e:
            logging.error(f"Error fetching entity ID from Shotgun: {e}")
            return None

    def get_task_id(self, entity_id, task_name):
        """
        Retrieves the task ID based on the entity ID and task name from Shotgun.

        :param entity_id: The entity ID (e.g., shot, asset).
        :param task_name: The task name (e.g., "Animation", "Lighting").
        :return: The task ID, or None if not found.
        """
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            return None

        try:
            if not self.sg:
                logging.error("Shotgun API session is not available.")
                return None

            task = self.sg.find_one(
                "Task", [["entity", "is", {"type": self.entity_type, "id": entity_id}]]
            )
            return task["id"] if task else None
        except Exception as e:
            logging.error(f"Error fetching task ID from Shotgun: {e}")
            return None

    def get_artist_id(self, artist_name):
        """
        Retrieves the artist ID based on the artist's name from Shotgun.

        :param artist_name: The name of the artist.
        :return: The artist ID, or None if not found.
        """
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            return None

        try:
            if not self.sg:
                logging.error("Shotgun API session is not available.")
                return None

            artist = self.sg.find_one("HumanUser", [["name", "is", artist_name]])
            return artist["id"] if artist else None
        except Exception as e:
            logging.error(f"Error fetching artist ID from Shotgun: {e}")
            return None

    def insert_version(self, version_name, video_path, comment):
        """
        Inserts a version into Shotgun, associating it with a specific entity and uploading a video.

        :param version_name: The version name (e.g., "v001", "v002", etc.).
        :param video_path: The path to the video file to be uploaded.
        :param comment: A comment describing the version.
        """
        if not SHOTGUN_API_AVAILABLE:
            logging.error("Shotgun API is not available.")
            return None

        try:
            if not self.sg:
                logging.error("Shotgun API session is not available.")
                return None

            # Create version
            data = {
                "project": {"type": "Project", "id": self.project_id},
                "code": version_name,
                "entity": {"type": self.entity_type, "id": self.entity_id},
                "sg_uploaded_movie": video_path,
                "sg_task": {
                    "type": "Task",
                    "id": self.get_task_id(self.entity_id, "Render"),
                },  # Example task type
                "sg_status_list": "rev",  # This status may vary
            }

            # Create the version entry
            self.sg.create("Version", data)
            logging.info(f"Version '{version_name}' inserted into Shotgun.")

            # Add comment
            self.sg.create(
                "Note",
                {
                    "content": comment,
                    "entity": {"type": self.entity_type, "id": self.entity_id},
                    "project": {"type": "Project", "id": self.project_id},
                },
            )
            logging.info(f"Added comment: '{comment}'")

        except Exception as e:
            logging.error(f"Error inserting version into Shotgun: {e}")


def main():
    """
    Main function to test the ShotgunTracking class.
    """
    environment = Environment(
        project_name="pipeline_test", entity_name="MyAsset", task_name="render"
    )
    shotgun_tracker = ShotgunTracking(environment)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = shotgun_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = shotgun_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")

    # Test fetching artist ID by name
    artist_name = "John Doe"  # Replace with an actual artist name
    artist_id = shotgun_tracker.get_artist_id(artist_name)
    logging.info(f"Artist ID for '{artist_name}': {artist_id}")

    # Test inserting a version
    version_name = "v001"
    video_path = "/path/to/your/video.mov"  # Replace with an actual video path
    comment = "Initial version"
    shotgun_tracker.insert_version(version_name, video_path, comment)


if __name__ == "__main__":
    main()
