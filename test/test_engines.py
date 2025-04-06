import unittest
import os
import time

from dailies.engine import FFmpegEngine, RVIOEngine, NukeEngine


class TestVideoEngines(unittest.TestCase):

    def test_ffmpeg_create_video(self):
        ffmpeg_engine = FFmpegEngine()

        # Define test paths
        input_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-%03d.jpg"  # Example image sequence
        output_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-v001.mov"
        resolution = (1920, 1080)  # Resolution for the output video
        extension = "mov"  # Output video format
        fps = 30  # Frames per second for the video
        options = {
            "y": None,  # Overwrite the output file
        }
        slate_data = None  # No slate for this test

        # Call the method that uses FFmpeg to create the media
        ffmpeg_engine.create_media(
            input_path, output_path, resolution, extension, fps, options, slate_data
        )

        # Check if the output file exists
        time.sleep(2)  # Wait a bit for the file to be generated
        self.assertTrue(
            os.path.exists(output_path), f"Output file not found: {output_path}"
        )

    def test_rvio_create_video(self):
        rvio_engine = RVIOEngine()

        # Define test paths
        input_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-%03d.jpg"  # Example image sequence
        output_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-v001.mov"
        resolution = (1920, 1080)  # Resolution for the output video
        extension = "mov"  # Output video format
        fps = 30  # Frames per second for the video
        options = None
        slate_data = None  # No slate for this test

        # Call the method that uses RVIO to create the media
        rvio_engine.create_media(
            input_path, output_path, resolution, extension, fps, options, slate_data
        )

        # Check if the output file exists
        time.sleep(2)  # Wait a bit for the file to be generated
        self.assertTrue(
            os.path.exists(output_path), f"Output file not found: {output_path}"
        )

    def test_nuke_create_video(self):
        nuke_engine = NukeEngine()

        # Define test paths
        input_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-%03d.jpg"  # Example image sequence
        output_path = "C:/Users/info/Downloads/ezgif-split/ezgif-frame-v001.mov"
        resolution = (1920, 1080)  # Resolution for the output video
        extension = "mov"  # Output video format
        fps = 30  # Frames per second for the video
        options = None
        slate_data = None  # No slate for this test

        # Call the method that uses Nuke to create the media
        nuke_engine.create_media(
            input_path, output_path, resolution, extension, fps, options, slate_data
        )

        # Check if the output file exists
        time.sleep(2)  # Wait a bit for the file to be generated
        self.assertTrue(
            os.path.exists(output_path), f"Output file not found: {output_path}"
        )


if __name__ == "__main__":
    unittest.main()
