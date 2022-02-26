import unittest
from datetime import  time
from entry import Entry


class TestEntry(unittest.TestCase):
    
    def setUp(self):
        self.entry = Entry(entry={'begin': '0901', 'end': '1600'})

    def test_can_instanciate_entry(self):
        self.assertIsInstance(self.entry, Entry)
        self.assertIsInstance(self.entry.begin, time)
        self.assertEqual(self.entry.begin, time(9,1))
        self.assertTrue(callable(self.entry.set_begin_time))
        self.assertTrue(callable(self.entry.set_end_time))

