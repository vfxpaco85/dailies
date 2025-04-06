import unittest
from unittest.mock import patch, Mock

from dailies.environment import Environment
from dailies.tracking import KitsuTracking


class TestKitsuTracking(unittest.TestCase):

    @patch("requests.post")
    def test_insert_version(self, mock_post):
        """
        Test the insert_version method for the Kitsu API.
        """
        mock_response = Mock()
        mock_response.status_code = 201  # Simulate a successful response
        mock_post.return_value = mock_response

        kitsu_tracking = KitsuTracking(Environment())

        # Define test inputs
        project_id = 123
        version_number = 1
        video_path = "/path/to/video.mov"

        kitsu_tracking.insert_version(version_number, video_path)

        mock_post.assert_called_once_with(
            f"https://your-kitsu-instance.com/api/v1/projects/{project_id}/versions",
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

        self.assertEqual(mock_response.status_code, 201)

    @patch("requests.post")
    def test_insert_version_failure(self, mock_post):
        """
        Test the insert_version method for the Kitsu API failure scenario.
        """
        mock_response = Mock()
        mock_response.status_code = 400  # Simulate a failure response
        mock_post.return_value = mock_response

        kitsu_tracking = KitsuTracking(Environment())

        version_number = 1
        video_path = "/path/to/video.mov"

        kitsu_tracking.insert_version(version_number, video_path)

        self.assertEqual(mock_response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
