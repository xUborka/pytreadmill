import unittest
from treadmill_data import TreadmillData

class TestTreadmillData(unittest.TestCase):
    def test_empty_init(self):
        tmd = TreadmillData()
        self.assertEqual(tmd.time, 0)
        self.assertEqual(tmd.recording, -1)
        self.assertEqual(tmd.velocity, 0)
        self.assertEqual(tmd.absPosition, 0)
        self.assertEqual(tmd.lap, 0)
        self.assertEqual(tmd.relPosition, 0)
        self.assertEqual(tmd.lick, 0)
        self.assertEqual(tmd.initialized, 0)
        self.assertListEqual(tmd.portStates, [0, 0, 0])
    
    def test_init_with_values(self):
        tmd = TreadmillData(1, 2, 3, 4, 5, 6, 7, 8, [1, 2, 3])
        self.assertEqual(tmd.time, 1)
        self.assertEqual(tmd.recording, 2)
        self.assertEqual(tmd.velocity, 3)
        self.assertEqual(tmd.absPosition, 4)
        self.assertEqual(tmd.lap, 5)
        self.assertEqual(tmd.relPosition, 6)
        self.assertEqual(tmd.lick, 7)
        self.assertEqual(tmd.initialized, 8)
        self.assertListEqual(tmd.portStates, [1, 2, 3])
    
    def test_invalidate(self):
        tmd = TreadmillData(1, 2, 3, 4, 5, 6, 7, 8, [1, 2, 3])
        tmd.invalidate()
        self.assertEqual(tmd.time, 0)
        self.assertEqual(tmd.recording, -1)
        self.assertEqual(tmd.velocity, 0)
        self.assertEqual(tmd.absPosition, 0)
        self.assertEqual(tmd.lap, 0)
        self.assertEqual(tmd.relPosition, 0)
        self.assertEqual(tmd.lick, 0)
        self.assertEqual(tmd.initialized, 0)
        self.assertListEqual(tmd.portStates, [0, 0, 0])
    
    def test_to_string(self):
        tmd = TreadmillData(1, 2, 3, 4, 5, 6, 7, 8, [1, 2, 3])
        # 2 = Recording
        # 8 = Initialized
        # [1,2,3] = Port States
        # Those are not required
        self.assertEqual(str(tmd), '1,3,4,5,6,7')