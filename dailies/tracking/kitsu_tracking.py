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

        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            self.session = None
            return

        try:
            # Log in and assign the session
            self.session = gazu.log_in(TRACKING_LOGIN_USR, TRACKING_LOGIN_PWD)
            if self.session:
                logging.info("Logged into Kitsu via gazu.")
            else:
                logging.error("Failed to log in. Session not available.")
        except Exception as e:
            logging.error(f"Failed to login to Kitsu with gazu: {e}")

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Kitsu.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return None

        if not self.session:
            logging.error("Session not available. Please login first.")
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
        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return None

        if not self.session:
            logging.error("Session not available. Please login first.")
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
        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return None

        if not self.session:
            logging.error("Session not available. Please login first.")
            return None

        try:
            # Fetch the task type by name
            task_type = gazu.task.get_task_type_by_name(task_name)
            if not task_type:
                logging.error(f"Task type '{task_name}' not found.")
                return None

            task_type_id = task_type["id"]

            # Fetch tasks for the given entity and task type
            tasks = gazu.task.all_tasks_for_entity_and_task_type(
                entity_id, task_type_id
            )

            if not tasks:
                logging.warning(
                    f"No tasks found for entity {entity_id} with task type {task_name}."
                )
                return None

            # Assuming only one task is returned, return the first task ID
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
        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return None

        if not self.session:
            logging.error("Session not available. Please login first.")
            return None

        try:
            # Get all people (artists)
            people = gazu.person.all_persons()

            # Iterate over the people and find the artist by name
            for person in people:

                # Check for exact match of name (case insensitive)
                if person.get("full_name", "").lower() == artist_name.lower():
                    return person["id"]

            logging.warning(f"Artist '{artist_name}' not found.")
            return None

        except Exception as e:
            logging.error(f"Error fetching artist ID for '{artist_name}': {e}")
            return None

    def insert_version(self, version_name, video_path, comment):
        """
        Creates a version (daily) for a shot and uploads a QuickTime preview to Kitsu.

        :param version_name: The version name (e.g., "v001", "v002", etc.).
        :param video_path: The full path to the QuickTime file.
        :param comment: A comment describing the version being uploaded (e.g., "Animation pass 1").
        """
        if not self.session:
            logging.error("Session not available. Please login first.")
            return None

        if not GAZU_AVAILABLE:
            logging.error("Gazu module is not available.")
            return None

        try:
            # Get project
            project = gazu.project.get_project(self.project_id)

            # Get entity (e.g. shot)
            entity = gazu.shot.get_shot(self.entity_id)

            if not entity:
                logging.error("Entity (shot) not found.")
                return None

            # Get task type
            task_type = gazu.task.get_task_type_by_name(self.environment.task_name)
            if not task_type:
                logging.error(f"Task type '{self.environment.task_name}' not found.")
                return None

            # Get task
            task_id = self.get_task_id(self.entity_id, task_type["name"])

            if not task_id:
                logging.warning("No task found for this entity. Creating default one.")
                task = gazu.task.new_task(self.entity_id, task_type)
                task_id = task["id"]

            # Ensure task_id is a string
            task_id = str(task_id)

            # Now create the preview
            preview = gazu.task.create_preview(
                task_id,  # Pass task_id (string) instead of task dict
                comment,  # Pass the comment as string
            )

            logging.info(f"Created version {version_name} for task {task_id}")

            # Upload preview file (ensure this method is correct for file upload)
            gazu.files.upload_preview_file(preview, video_path)
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
    version_number = 1
    video_path = "/path/to/video.mov"  # Update path here
    kitsu_tracker.insert_version(version_number, video_path, "foobar")


if __name__ == "__main__":
    main()
