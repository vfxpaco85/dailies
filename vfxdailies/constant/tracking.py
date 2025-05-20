import os
import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE_PATH),
    ]
)

# Choose the tracking engine (e.g., 'shotgun', 'ftrack', 'kitsu')
TRACKING_ENGINE = os.getenv("TRACKING_ENGINE", "shotgun")  # Default to 'shotgun' if not set in environment

# Tracking credentials
# If not set via environment variables, fallback to default values
TRACKING_LOGIN_USR = os.getenv("TRACKING_LOGIN_USR", "USR")  # Set via environment or change here
TRACKING_LOGIN_PWD = os.getenv("TRACKING_LOGIN_PWD", "PWD")  # Set via environment or change here
TRACKING_API_TOKEN = os.getenv("TRACKING_API_TOKEN", "PWD")  # Set via environment or change here

# Log warnings if credentials are missing or using default values
if TRACKING_LOGIN_USR == "USR":
    logger.warning("Tracking username is not set or is using the default value: 'USR'. Please set 'TRACKING_LOGIN_USER' in your environment variables.")
if TRACKING_LOGIN_PWD == "PWD":
    logger.warning("Tracking password is not set or is using the default value: 'PWD'. Please set 'TRACKING_LOGIN_PWD' in your environment variables.")
if TRACKING_API_TOKEN == "PWD":
    logger.warning("Tracking API token is not set or is using the default value: 'PWD'. Please set 'TRACKING_API_TOKEN' in your environment variables.")

# URLs for tracking engines
API_URLS = {
    "shotgun": "https://your-shotgun-instance.com/api/v1",
    "ftrack": "https://your-ftrack-instance.com/api/v1",
    "kitsu": "https://your-kitsu-instance.com/api/v1",
}

# Dictionary to map tracking software names to their respective class names
TRACKING_SOFTWARE_CLASSES = {
    "shotgun": "dailies.tracking.shotgun_tracking.ShotgunTracking",
    "ftrack": "dailies.tracking.ftrack_tracking.FtrackTracking",
    "kitsu": "dailies.tracking.kitsu_tracking.KitsuTracking",
}

# Log the chosen tracking engine and its corresponding API URL
logger.info(f"Using tracking engine: {TRACKING_ENGINE}")

if TRACKING_ENGINE in API_URLS:
    logger.info(f"API URL for {TRACKING_ENGINE}: {API_URLS[TRACKING_ENGINE]}")
else:
    logger.warning(f"Unknown tracking engine '{TRACKING_ENGINE}' specified. Defaulting to 'shotgun'.")
    logger.info(f"API URL for 'shotgun': {API_URLS['shotgun']}")
