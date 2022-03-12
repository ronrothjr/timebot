import unittest
from day import Day
from datetime import time


class TestDay(unittest.TestCase):
    
    def setUp(self):
        self.day = Day({'weekday': 'Monday', 'entries': {'0900': {'begin': '0900', 'end': '1600'}}})

    def test_can_instantiate_hours(self):
        self.assertIsInstance(self.day, Day)
        self.assertIsInstance(self.day.tasks, dict)
        self.assertTrue(callable(self.day.add_tasks))

    def test_can_add_tasks(self):
        self.day.add_tasks({'0900': {'begin': '0900', 'end': '1600'}})
        task = self.day.tasks.get('0900')
        self.assertEqual(task.begin, time(9))
