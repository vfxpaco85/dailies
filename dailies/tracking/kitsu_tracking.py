import logging
import requests

from dailies.constant.tracking import TRACKING_LOGIN_USER, TRACKING_API_TOKEN
from dailies.environment import Environment
from dailies.tracking.tracking import TrackingSoftware


class KitsuTracking(TrackingSoftware):
    """
    Kitsu-specific implementation of the TrackingSoftware class.
    Handles interactions with Kitsu's API.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the KitsuTracking instance.

        :param environment: The environment instance that contains project and entity details.
        """
        super().__init__(environment)

    def insert_version(self, version_number, video_path):
        """
        Inserts a version into Kitsu.

        :param version_number: The version number to be created.
        :param video_path: The path to the video file to be uploaded.
        """
        headers = self._get_headers()

        data = {
            "data": {
                "type": "versions",
                "attributes": {
                    "name": f"Version {version_number}",
                    "project-id": self.project_id,
                    "video-path": video_path,
                },
            }
        }

        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            if response.status_code == 201:
                logging.info(f"Version {version_number} inserted into Kitsu.")
            else:
                logging.error(f"Error inserting version into Kitsu: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while connecting to Kitsu: {e}")

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Kitsu.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        headers = self._get_headers()
        try:
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                project = response.json().get("data", [])[0]
                return project["id"] if project else None
            else:
                logging.error(
                    f"Error fetching project ID from Kitsu: {response.status_code} - {response.text}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while connecting to Kitsu: {e}")
            return None

    def get_entity_id(self, entity_name, entity_type=None):
        """
        Retrieves the entity ID based on the entity name and entity type from Kitsu.

        :param entity_name: The entity name to search for.
        :param entity_type: The entity type to use (defaults to the one in the environment).
        :return: The entity ID, or None if not found.
        """
        headers = self._get_headers()

        try:
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                entity = response.json().get("data", [])[0]
                return entity["id"] if entity else None
            else:
                logging.error(
                    f"Error fetching entity ID from Kitsu: {response.status_code} - {response.text}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while connecting to Kitsu: {e}")
            return None


def main():
    """
    Main function to test the KitsuTracking class.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Assume we have an environment object
    environment = Environment(
        api_url="https://your-kitsu-instance.kitsuapp.com",  # Replace with your Kitsu API URL
        project_id=1,  # Replace with actual project ID
        entity_type="Asset",  # Replace with actual entity type
        entity_id=1,  # Replace with actual entity ID
    )

    # Create a KitsuTracking instance
    kitsu_tracker = KitsuTracking(environment)

    # Test inserting a version
    version_number = 1
    video_path = "/path/to/video/file.mov"  # Replace with an actual video file path
    kitsu_tracker.insert_version(version_number, video_path)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = kitsu_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = kitsu_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")


if __name__ == "__main__":
    main()
