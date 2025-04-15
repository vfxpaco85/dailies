import importlib
import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.constant.engine import ENGINE_CLASSES
from dailies.constant.tracking import TRACKING_SOFTWARE_CLASSES
from dailies.environment import Environment

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


class VideoEngineFactory:
    """
    Factory class that creates the appropriate video engine.
    """

    @staticmethod
    def get_video_engine(engine_name: str):
        """
        Factory method to return the appropriate video engine.

        :param engine_name: 'ffmpeg', 'rvio', 'nuke', 'nuke-template', or potentially more.
        :return: An instance of the correct video engine.
        """
        logger.info(f"Requesting video engine for: {engine_name}")

        engine_class_name = ENGINE_CLASSES.get(engine_name)

        if not engine_class_name:
            logger.error(f"Unsupported engine type: {engine_name}")
            raise ValueError(f"Unsupported engine type: {engine_name}")

        # Dynamically import the module that contains the engine class
        try:
            # Attempt to split the full class path into module and class
            if "." not in engine_class_name:
                logger.error(
                    f"Invalid engine class name: {engine_class_name}. Expected 'module.class' format."
                )
                raise ValueError(
                    f"Invalid engine class name: {engine_class_name}. Expected 'module.class' format."
                )

            module_name, class_name = engine_class_name.rsplit(".", 1)
            logger.info(f"Importing module: {module_name}")
            module = importlib.import_module(module_name)
            engine_class = getattr(module, class_name)
            logger.info(f"Successfully imported {class_name} from {module_name}")

        except (ValueError, ImportError, AttributeError) as e:
            logger.error(f"Error importing class {engine_class_name}: {e}")
            raise ValueError(f"Error importing class {engine_class_name}: {e}")

        logger.info(f"Returning instance of {engine_class_name}")
        return engine_class()  # Instantiate and return the video engine


class TrackingSoftwareFactory:
    """
    Factory class that creates the appropriate tracking software instance.
    """

    @staticmethod
    def get_tracking_software(
        tracking_software_name: str, environment: Environment = None
    ):
        """
        Factory method to return the appropriate tracking software instance.

        :param tracking_software_name: Name of the tracking software (e.g., "shotgun", "ftrack", "kitsu", or more).
        :param environment: An optional Environment object. If not provided, a new one will be created.
        :return: An instance of the correct tracking software.
        """
        logger.info(f"Requesting tracking software for: {tracking_software_name}")

        tracking_class_name = TRACKING_SOFTWARE_CLASSES.get(tracking_software_name)

        if not tracking_class_name:
            logger.error(f"Unsupported tracking software: {tracking_software_name}")
            raise ValueError(f"Unsupported tracking software: {tracking_software_name}")

        # Dynamically import the module that contains the tracking software class
        try:
            if "." not in tracking_class_name:
                logger.error(
                    f"Invalid tracking software class name: {tracking_class_name}. Expected 'module.class' format."
                )
                raise ValueError(
                    f"Invalid tracking software class name: {tracking_class_name}. Expected 'module.class' format."
                )

            module_name, class_name = tracking_class_name.rsplit(".", 1)
            logger.info(f"Importing module: {module_name}")
            module = importlib.import_module(module_name)
            tracking_class = getattr(module, class_name)
            logger.info(f"Successfully imported {class_name} from {module_name}")

        except (ValueError, ImportError, AttributeError) as e:
            logger.error(f"Error importing class {tracking_class_name}: {e}")
            raise ValueError(f"Error importing class {tracking_class_name}: {e}")

        # Use provided Environment or create one
        env = environment or Environment()

        logger.info(f"Returning instance of {tracking_class_name} with Environment")
        return tracking_class(env)


# Example usage
if __name__ == "__main__":
    # Test video engine
    video_engine_name = "nuke"  # Example: "ffmpeg", "rvio", "nuke", "nuke-template"
    logger.info(f"Testing with video engine: {video_engine_name}")
    video_engine = VideoEngineFactory.get_video_engine(video_engine_name)
    logger.info(f"Using video engine: {video_engine}")

    # Test tracking software
    tracking_software_name = "shotgun"  # Example: "shotgun", "ftrack", etc.
    logger.info(f"Testing with tracking software: {tracking_software_name}")
    tracking_software = TrackingSoftwareFactory.get_tracking_software(
        tracking_software_name
    )
    logger.info(f"Using tracking software: {tracking_software}")
