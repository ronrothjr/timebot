import unittest
from day import Day
from datetime import time


class TestDay(unittest.TestCase):
    
    def setUp(self):
        self.day = Day({'weekday': 'Monday', 'entries': {'0900': {'begin': '0900', 'end': '1600'}}})

    def test_can_instantiate_hours(self):
        self.assertIsInstance(self.day, Day)
        self.assertIsInstance(self.day.entries, dict)
        self.assertTrue(callable(self.day.add_entries))

    def test_can_add_entries(self):
        self.day.add_entries({'0900': {'begin': '0900', 'end': '1600'}})
        entry = self.day.entries.get('0900')
        self.assertEqual(entry.begin, time(9))
