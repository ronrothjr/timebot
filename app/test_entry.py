import unittest, os
from datetime import  time
from entry import Entry


os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"


class TestEntry(unittest.TestCase):
    
    def setUp(self):
        self.entry = Entry({'begin': '0901', 'end': '1600'})

    def test_can_instanciate_entry(self):
        self.assertIsInstance(self.entry, Entry)
        self.assertIsInstance(self.entry.begin, time)
        self.assertEqual(self.entry.begin, time(9,1))

