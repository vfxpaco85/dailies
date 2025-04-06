import logging

from dailies.constant.tracking import TRACKING_LOGIN_USER, TRACKING_API_TOKEN
from dailies.environment import Environment
from dailies.tracking.tracking import TrackingSoftware


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

    def insert_version(self, version_number, video_path):
        """
        Inserts a version into Ftrack.

        :param version_number: The version number to be created.
        :param video_path: The path to the video file to be uploaded.
        """
        try:
            import ftrack_api
        except ImportError:
            logging.error(
                "ftrack_api not found. Ftrack-related functionality will be disabled."
            )
            ftrack_api = None

        if ftrack_api:
            session = ftrack_api.Session()

            try:
                project = session.query(
                    f"select * from Project where id={self.project_id}"
                ).one()

                version = ftrack_api.Entity("Version")
                version["name"] = f"Version {version_number}"
                version["project"] = project
                version["file"] = video_path

                session.add(version)
                session.commit()
                logging.info(f"Version {version_number} inserted into Ftrack.")
            except Exception as e:
                logging.error(f"Error inserting version into Ftrack: {e}")
        else:
            logging.error("Ftrack API is not available, unable to insert version.")

    def get_project_id(self, project_name):
        """
        Retrieves the project ID based on the project name from Ftrack.

        :param project_name: The project name to search for.
        :return: The project ID, or None if not found.
        """
        try:
            import ftrack_api

            session = ftrack_api.Session()
            project = session.query(
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
        try:
            import ftrack_api

            session = ftrack_api.Session()
            entity_type = entity_type or self.entity_type
            entity = session.query(
                f"select * from {entity_type} where name='{entity_name}'"
            ).one()
            return entity["id"] if entity else None
        except Exception as e:
            logging.error(f"Error fetching entity ID from Ftrack: {e}")
            return None


def main():
    """
    Main function to test the FtrackTracking class.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Assume we have an environment object
    environment = Environment(
        api_url="https://your-ftrack-instance.ftrackapp.com",
        project_id=1,  # Replace with actual project ID
        entity_type="Asset",  # Replace with actual entity type
        entity_id=1,  # Replace with actual entity ID
    )

    # Create a FtrackTracking instance
    ftrack_tracker = FtrackTracking(environment)

    # Test inserting a version
    version_number = 1
    video_path = "/path/to/video/file.mov"  # Replace with an actual video file path
    ftrack_tracker.insert_version(version_number, video_path)

    # Test fetching project ID
    project_name = "MyProject"  # Replace with an actual project name
    project_id = ftrack_tracker.get_project_id(project_name)
    logging.info(f"Project ID for '{project_name}': {project_id}")

    # Test fetching entity ID
    entity_name = "MyAsset"  # Replace with an actual entity name
    entity_id = ftrack_tracker.get_entity_id(entity_name)
    logging.info(f"Entity ID for '{entity_name}': {entity_id}")


if __name__ == "__main__":
    main()
