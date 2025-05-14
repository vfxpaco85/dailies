import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.constant.tracking import (
    API_URLS,
    TRACKING_ENGINE,
    TRACKING_LOGIN_USR,
    TRACKING_LOGIN_PWD,
)
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

try:
    import gazu

    GAZU_AVAILABLE = True
except ImportError as e:
    GAZU_AVAILABLE = False
    logging.error(f"Failed to import gazu module: {e}")


class KitsuTracking(TrackingSoftware):
    """
    Kitsu-specific implementation of the TrackingSoftware class.
    Handles interactions with Kitsu's API using gazu.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the KitsuTracking instance.

        :param environment: The environment instance that contains project and entity details.
        """
        super().__init__(environment)
        self.session = None

        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return

        try:
            gazu.client.set_host(API_URLS.get(TRACKING_ENGINE))
            self.session = gazu.log_in(TRACKING_LOGIN_USR, TRACKING_LOGIN_PWD)
            if self.session:
                logging.info("Logged into Kitsu via gazu.")
            else:
                logging.error("Failed to log in. Session not available.")
        except Exception as e:
            logging.error(f"Failed to login to Kitsu with gazu: {e}")

    def _validate(self):
        """
        Validates that the gazu module is available and a session has been established.

        :return: True if both conditions are met, False otherwise.
        """
        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return False
        if not self.session:
            logging.error("Session not available. Please login first.")
            return False
        return True

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Kitsu.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        if not self._validate():
            return None

        try:
            project = gazu.project.get_project_by_name(project_name)
            if project:
                return project["id"]
            else:
                logging.warning(f"Project '{project_name}' not found in Kitsu.")
                return None
        except Exception as e:
            logging.error(f"Error fetching project ID from Kitsu via gazu: {e}")
            return None

    def get_entity_id(self, entity_name, entity_type="Shot"):
        """
        Retrieves the entity ID based on the entity name and type using gazu.

        :param entity_name: The name of the entity (e.g., shot name, asset name, or sequence name).
        :param entity_type: "Shot", "Asset", or "Sequence"
        :return: The entity ID, or None if not found.
        """
        if not self._validate():
            return None

        try:
            if not self.project_id:
                logging.error("Project not found. Cannot fetch entity.")
                return None

            if entity_type.lower() == "shot":
                entities = gazu.shot.all_shots_for_project(self.project_id)
            elif entity_type.lower() == "asset":
                entities = gazu.asset.all_assets_for_project(self.project_id)
            elif entity_type.lower() == "sequence":
                entities = gazu.sequence.all_sequences_for_project(self.project_id)
            else:
                logging.error(f"Unsupported entity type: {entity_type}")
                return None

            for entity in entities:
                if entity["name"] == entity_name:
                    return entity["id"]

            logging.warning(f"{entity_type} '{entity_name}' not found in project.")
            return None

        except Exception as e:
            logging.error(f"Error fetching entity ID via gazu: {e}")
            return None

    def get_task_id(self, entity_id, task_name):
        """
        Retrieves the task ID for a given entity and task type name.

        :param entity_id: The entity ID (shot, asset, sequence, etc.).
        :param task_name: The task type name (e.g., "Animation", "Lighting").
        :return: The task ID, or None if not found.
        """
        if not self._validate():
            return None

        try:
            task_type = gazu.task.get_task_type_by_name(task_name)
            if not task_type:
                logging.error(f"Task type '{task_name}' not found.")
                return None

            tasks = gazu.task.all_tasks_for_entity_and_task_type(
                entity_id, task_type["id"]
            )
            if not tasks:
                logging.warning(
                    f"No tasks found for entity {entity_id} with task type {task_name}."
                )
                return None

            return tasks[0]["id"]
        except Exception as e:
            logging.error(f"Error fetching task ID: {e}")
            return None

    def get_artist_id(self, artist_name):
        """
        Retrieves the artist ID based on the artist's name.

        :param artist_name: The name of the artist (person).
        :return: The artist ID, or None if not found.
        """
        if not self._validate():
            return None

        try:
            people = gazu.person.all_persons()
            for person in people:
                if person.get("full_name", "").lower() == artist_name.lower():
                    return person["id"]

            logging.warning(f"Artist '{artist_name}' not found.")
            return None

        except Exception as e:
            logging.error(f"Error fetching artist ID for '{artist_name}': {e}")
            return None

    def insert_version(self, version_name, video_path, comment):
        """
        Creates a version (daily) for a shot, sequence, or asset and uploads a QuickTime preview to Kitsu.

        :param version_name: The version name (e.g., "v001", "v002", etc.).
        :param video_path: The full path to the QuickTime file.
        :param comment: A comment describing the version being uploaded.
        """
        if not self._validate():
            return None

        if not self.environment.entity_id and not self.environment.entity_name:
            logging.error("Missing entity_name in environment.")
            return None

        if not self.environment.task_id and not self.environment.task_name:
            logging.error("Missing task_name in environment.")
            return None

        try:

            if self.environment.entity_type == "shot":
                entity = gazu.shot.get_shot(self.environment.entity_id)
            elif self.environment.entity_type == "sequence":
                entity = gazu.sequence.get_sequence(self.environment.entity_id)
            elif self.environment.entity_type == "asset":
                entity = gazu.asset.get_asset(self.environment.entity_id)
            else:
                logging.error(
                    f"Unsupported entity type: {self.environment.entity_type}"
                )
                return None

            if not entity:
                logging.error(f"Entity ({self.environment.entity_type}) not found.")
                return None

            task_type = gazu.task.get_task_type_by_name(self.environment.task_name)
            if not task_type:
                logging.error(f"Task type '{self.environment.task_name}' not found.")
                return None

            task_id = self.get_task_id(self.environment.entity_id, task_type["name"])
            if not task_id:
                logging.warning(
                    f"No task found for {self.environment.entity_type}. Creating default one."
                )
                task = gazu.task.new_task(self.environment.entity_id, task_type)
            else:
                task = gazu.task.get_task(task_id)

            status = gazu.task.get_task_status(task["task_status_id"])

            file_string = f"\n\n<hr><b><u>FILE :</b></u><i>\n{str(video_path)}</i>\n"
            gazu_comment = gazu.task.add_comment(task, status, comment + file_string)

            preview = gazu.task.add_preview(task, gazu_comment, video_path)
            if preview:
                logging.info(f"Created version {version_name} for task {task['id']}")
                logging.info(f"Uploaded QuickTime preview for version {version_name}")

        except Exception as e:
            logging.error(f"Error inserting version into Kitsu: {e}")


def main():
    """
    Main function to test the KitsuTracking class.
    """
    environment = Environment(project_name="pipeline_test")
    kitsu_tracker = KitsuTracking(environment)

    # Test fetching project ID
    project_name = "pipeline_test"
    project_id = kitsu_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MR_LGP_01_0320"
    entity_id = kitsu_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")

    # Test fetching task ID
    task_name = "fx"
    task_id = kitsu_tracker.get_task_id(entity_id, task_name)
    logging.info(f"Task ID for '{task_name}': {task_id}")

    # Test fetching artist ID by name
    artist_name = "User"  # Update user here
    artist_id = kitsu_tracker.get_artist_id(artist_name)
    logging.info(f"Artist ID for '{artist_name}': {artist_id}")

    # Test inserting a version (daily)
    environment = Environment(
        project_name="pipeline_test",
        entity_name="MR_LGP_01_0320",
        entity_type="shot",
        task_name="fx",
    )
    kitsu_tracker = KitsuTracking(environment)
    version_name = "v001"
    video_path = "/path/to/video.mov"  # Update path here
    kitsu_tracker.insert_version(version_name, video_path, "foobar")


if __name__ == "__main__":
    main()
