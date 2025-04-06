import unittest
from unittest.mock import patch, Mock

from dailies.environment import Environment
from dailies.tracking import ShotgunTracking


class TestShotgunTracking(unittest.TestCase):

    @patch("requests.post")
    def test_insert_version(self, mock_post):
        """
        Test the insert_version method for the Shotgun API.
        """

        # Mock the response from the Shotgun API
        mock_response = Mock()
        mock_response.status_code = 201  # Simulate a successful response
        mock_post.return_value = mock_response

        # Instantiate ShotgunTracking
        shotgun_tracking = ShotgunTracking(Environment())

        # Define test inputs
        project_id = 123
        version_number = 1
        video_path = "/path/to/video.mov"

        # Call the method we're testing
        shotgun_tracking.insert_version(version_number, video_path)

        # Assert that requests.post was called once with the expected arguments
        mock_post.assert_called_once_with(
            f"https://your-shotgun-instance.com/api/v1/projects/{project_id}/versions",
            json={
                "data": {
                    "type": "versions",
                    "attributes": {
                        "name": f"Version {version_number}",
                        "project-id": project_id,
                        "video-path": video_path,
                    },
                }
            },
            headers={
                "Authorization": "Bearer your_api_token",
                "Content-Type": "application/json",
            },
        )

        # Also assert that the Shotgun version was inserted (successful API call)
        self.assertEqual(mock_response.status_code, 201)

    @patch("requests.post")
    def test_insert_version_failure(self, mock_post):
        """
        Test the insert_version method for the Shotgun API failure scenario.
        """

        # Simulate a failure (non-201 response)
        mock_response = Mock()
        mock_response.status_code = 400  # Simulate a bad request response
        mock_post.return_value = mock_response

        # Instantiate ShotgunTracking
        shotgun_tracking = ShotgunTracking(Environment())

        # Define test inputs
        version_number = 1
        video_path = "/path/to/video.mov"

        # Call the method
        shotgun_tracking.insert_version(version_number, video_path)

        # Check that the mock response has the expected status code
        self.assertEqual(mock_response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
