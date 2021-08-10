import unittest
# from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject
from positionTrigger import PositionTriggerWorker, PositionTriggerData
# from Port import Port


class TestPositionTrigerData(unittest.TestCase):
    def test_empty_init(self):
        dummy_data = PositionTriggerData()
        self.assertEqual(dummy_data.port, None)
        self.assertEqual(dummy_data.thread, None)
        self.assertFalse(dummy_data.isActive)
        self.assertEqual(dummy_data.start, 0)
        self.assertEqual(dummy_data.retention, 0)
        self.assertEqual(dummy_data.window, 0)

    def test_init(self):
        dummy_port = None  # Port('A', None, None, None) --> TODO: Fails, Test Port First
        dummy_data = PositionTriggerData(dummy_port)
        self.assertEqual(dummy_data.port, None)
        self.assertEqual(dummy_data.thread, None)
        self.assertFalse(dummy_data.isActive)
        self.assertEqual(dummy_data.start, 0)
        self.assertEqual(dummy_data.retention, 0)
        self.assertEqual(dummy_data.window, 0)
