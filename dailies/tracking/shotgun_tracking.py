import logging

from dailies.constant.tracking import TRACKING_LOGIN_USER, TRACKING_API_TOKEN
from dailies.environment import Environment
from dailies.tracking.tracking import TrackingSoftware


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

    def insert_version(self, version_number, video_path):
        """
        Inserts a version into Shotgun, associating it with a specific entity.

        :param version_number: The version number to be created.
        :param video_path: The path to the video file to be uploaded.
        """
        try:
            import shotgun_api3
        except ImportError:
            logging.error(
                "shotgun_api3 not found. Shotgun-related functionality will be disabled."
            )
            shotgun_api3 = None

        if shotgun_api3:
            sg = shotgun_api3.Shotgun(
                self.api_url, login=TRACKING_LOGIN_USER, password=TRACKING_API_TOKEN
            )

            data = {
                "project": {"type": "Project", "id": self.project_id},
                "code": f"Version {version_number}",
                "entity": {"type": self.entity_type, "id": self.entity_id},
                "sg_uploaded_movie": video_path,
            }

            try:
                sg.create("Version", data)
                logging.info(f"Version {version_number} inserted into Shotgun.")
            except Exception as e:
                logging.error(f"Error inserting version into Shotgun: {e}")
        else:
            logging.error("Shotgun API is not available, unable to insert version.")

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Shotgun.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        try:
            import shotgun_api3

            sg = shotgun_api3.Shotgun(
                self.api_url, login=TRACKING_LOGIN_USER, password=TRACKING_API_TOKEN
            )
            project = sg.find_one("Project", [["name", "is", project_name]])
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
        try:
            import shotgun_api3

            sg = shotgun_api3.Shotgun(
                self.api_url, login=TRACKING_LOGIN_USER, password=TRACKING_API_TOKEN
            )
            entity_type = entity_type or self.entity_type
            entity = sg.find_one(entity_type, [["code", "is", entity_name]])
            return entity["id"] if entity else None
        except Exception as e:
            logging.error(f"Error fetching entity ID from Shotgun: {e}")
            return None


def main():
    """
    Main function to test the ShotgunTracking class.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Assume we have an environment object
    environment = Environment(
        api_url="https://your-shotgun-instance.shotgunstudio.com",
        project_id=1,  # Replace with actual project ID
        entity_type="Asset",  # Replace with actual entity type
        entity_id=1,  # Replace with actual entity ID
    )

    # Create a ShotgunTracking instance
    shotgun_tracker = ShotgunTracking(environment)

    # Test inserting a version
    version_number = 1
    video_path = "/path/to/video/file.mov"  # Replace with an actual video file path
    shotgun_tracker.insert_version(version_number, video_path)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = shotgun_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = shotgun_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")


if __name__ == "__main__":
    main()
