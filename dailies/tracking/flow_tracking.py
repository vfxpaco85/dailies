import logging

from dailies.constant.tracking import TRACKING_LOGIN_USER, TRACKING_API_TOKEN
from dailies.environment import Environment
from dailies.tracking.tracking import TrackingSoftware


class FlowTracking(TrackingSoftware):
    """
    Flow-specific implementation of the TrackingSoftware class.
    Handles interactions with Flow's API.
    """

    def __init__(self, environment: Environment):
        """
        Initializes the FlowTracking instance.

        :param environment: The environment instance that contains project and entity details.
        """
        super().__init__(environment)

    def insert_version(self, version_number, video_path):
        """
        Inserts a version into Flow.

        :param version_number: The version number to be created.
        :param video_path: The path to the video file to be uploaded.
        """
        # Ensure requests library is available
        try:
            import requests
        except ImportError:
            logging.warning(
                "requests library not found. Flow-related functionality may be disabled."
            )
            requests = None

        if requests:
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
                    logging.info(f"Version {version_number} inserted into Flow.")
                else:
                    logging.error(f"Error inserting version into Flow: {response.text}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error while connecting to Flow: {e}")
        else:
            logging.error(
                "Requests library is not available, unable to insert version."
            )

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Flow.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        # Ensure requests library is available
        try:
            import requests
        except ImportError:
            logging.warning(
                "requests library not found. Flow-related functionality may be disabled."
            )
            requests = None

        if requests:
            headers = self._get_headers()

            try:
                response = requests.get(self.api_url, headers=headers)
                if response.status_code == 200:
                    project = response.json().get("data", [])[0]
                    return project["id"] if project else None
                else:
                    logging.error(
                        f"Error fetching project ID from Flow: {response.status_code} - {response.text}"
                    )
                    return None
            except requests.exceptions.RequestException as e:
                logging.error(f"Error while connecting to Flow: {e}")
                return None
        else:
            logging.error(
                "Requests library is not available, unable to fetch project ID."
            )

    def get_entity_id(self, entity_name, entity_type=None):
        """
        Retrieves the entity ID based on the entity name and entity type from Flow.

        :param entity_name: The entity name to search for.
        :param entity_type: The entity type to use (defaults to the one in the environment).
        :return: The entity ID, or None if not found.
        """
        # Ensure requests library is available
        try:
            import requests
        except ImportError:
            logging.warning(
                "requests library not found. Flow-related functionality may be disabled."
            )
            requests = None

        if requests:
            headers = self._get_headers()

            try:
                response = requests.get(self.api_url, headers=headers)
                if response.status_code == 200:
                    entity = response.json().get("data", [])[0]
                    return entity["id"] if entity else None
                else:
                    logging.error(
                        f"Error fetching entity ID from Flow: {response.status_code} - {response.text}"
                    )
                    return None
            except requests.exceptions.RequestException as e:
                logging.error(f"Error while connecting to Flow: {e}")
                return None
        else:
            logging.error(
                "Requests library is not available, unable to fetch entity ID."
            )


def main():
    """
    Main function to test the FlowTracking class.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Assume we have an environment object
    environment = Environment(
        api_url="https://your-flow-instance.flowapp.com",  # Replace with your Flow API URL
        project_id=1,  # Replace with actual project ID
        entity_type="Asset",  # Replace with actual entity type
        entity_id=1,  # Replace with actual entity ID
    )

    # Create a FlowTracking instance
    flow_tracker = FlowTracking(environment)

    # Test inserting a version
    version_number = 1
    video_path = "/path/to/video/file.mov"  # Replace with an actual video file path
    flow_tracker.insert_version(version_number, video_path)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = flow_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = flow_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")


if __name__ == "__main__":
    main()
