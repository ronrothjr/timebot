import unittest
from hours import Hours
from datetime import time


class TestHours(unittest.TestCase):
    
    def setUp(self):
        self.hours = Hours({'0900': {'begin': '0900', 'end': '1600'}})

    def test_can_instantiate_hours(self):
        self.assertIsInstance(self.hours, Hours)
        self.assertIsInstance(self.hours.entries, dict)
        self.assertTrue(callable(self.hours.add_entries))

    def test_can_add_entries(self):
        self.hours.add_entries({'0900': {'begin': '0900', 'end': '1600'}})
        entry = self.hours.entries.get('0900')
        self.assertEqual(entry.begin, time(9))
