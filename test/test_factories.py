import unittest

from dailies.factory import VideoEngineFactory, TrackingSoftwareFactory
from dailies.engine import FFmpegEngine, RVIOEngine, NukeEngine
from dailies.tracking import (
    ShotgunTracking,
    FtrackTracking,
    KitsuTracking,
    FlowTracking,
)


class TestFactories(unittest.TestCase):

    def test_video_engine_factory(self):
        # Test that the VideoEngineFactory returns the correct engine instance.
        ffmpeg_engine = VideoEngineFactory.get_video_engine("ffmpeg")
        rvio_engine = VideoEngineFactory.get_video_engine("rvio")
        nuke_engine = VideoEngineFactory.get_video_engine("nuke")

        self.assertIsInstance(ffmpeg_engine, FFmpegEngine)
        self.assertIsInstance(rvio_engine, RVIOEngine)
        self.assertIsInstance(nuke_engine, NukeEngine)

        # Test invalid engine type
        with self.assertRaises(ValueError):
            VideoEngineFactory.get_video_engine("invalid_engine")

    def test_tracking_software_factory(self):
        # Test that the TrackingSoftwareFactory returns the correct software instance.
        shotgun_tracking = TrackingSoftwareFactory.get_tracking_software("shotgun")
        ftrack_tracking = TrackingSoftwareFactory.get_tracking_software("ftrack")
        kitsu_tracking = TrackingSoftwareFactory.get_tracking_software("kitsu")
        flow_tracking = TrackingSoftwareFactory.get_tracking_software("flow")

        self.assertIsInstance(shotgun_tracking, ShotgunTracking)
        self.assertIsInstance(ftrack_tracking, FtrackTracking)
        self.assertIsInstance(kitsu_tracking, KitsuTracking)
        self.assertIsInstance(flow_tracking, FlowTracking)

        # Test invalid software type
        with self.assertRaises(ValueError):
            TrackingSoftwareFactory.get_tracking_software("invalid_software")


if __name__ == "__main__":
    unittest.main()
