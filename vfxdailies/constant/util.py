import os
from datetime import datetime


def get_daily_tmp_directory(base_path: str) -> str:
    """
    Creates a directory for the current date under the given base path.
    If the directory already exists, it returns the existing directory path.
    Otherwise, it creates the directory.

    Ensures the base path exists before proceeding.

    Args:
        base_path (str): The base path where the daily directory should be created.
                         For example: "C:/Users/YourUser/AppData/Local/Temp"

    Returns:
        str: The full path to the daily directory. If the directory already exists,
             it returns the path to the existing directory.

    Raises:
        ValueError: If the base path does not exist.
        Exception: If the directory creation fails due to an exception.

    Example:
        base_path = "C:/Users/YourUser/AppData/Local/Temp"
        daily_tmp_dir = get_daily_tmp_directory(base_path)
        # Returns: C:/Users/YourUser/AppData/Local/Temp/daily-2025-04-04
    """
    # Check if the base path exists
    if not os.path.exists(base_path):
        print(f"ERROR: Base path does not exist: {base_path}")
        raise ValueError(f"Base path does not exist: {base_path}")

    # Generate daily directory name based on the current date
    daily_directory = f"daily-{datetime.now().strftime('%Y-%m-%d')}"
    tmp_directory = os.path.join(base_path, daily_directory)

    # Check if the directory exists, create it if not
    if not os.path.exists(tmp_directory):
        try:
            os.makedirs(tmp_directory)  # Create the directory
            print(f"Created new directory: {tmp_directory}")
        except Exception as e:
            # Print and raise an error if directory creation fails
            print(f"ERROR: Failed to create directory {tmp_directory}: {e}")
            raise
    else:
        print(f"Directory already exists: {tmp_directory}")

    return tmp_directory


def get_package_root_directory():
    """
    Returns the root directory of the package, which is the directory
    that contains the 'dailies' directory.

    Returns:
        str: The root directory path of the package, one level up from the 'dailies' directory.
    """
    # Get the directory containing the current file
    constant_directory_path = os.path.dirname(__file__)
    # Find the 'dailies' directory and go one level up
    return os.path.join(constant_directory_path[:constant_directory_path.rfind("dailies")])
