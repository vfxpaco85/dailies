import unittest

from .test_shotgun import TestShotgunTracking
from .test_ftrack import TestFtrackTracking
from .test_kitsu import TestKitsuTracking
from .test_flow import TestFlowTracking


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShotgunTracking))
    suite.addTest(unittest.makeSuite(TestFtrackTracking))
    suite.addTest(unittest.makeSuite(TestKitsuTracking))
    suite.addTest(unittest.makeSuite(TestFlowTracking))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
