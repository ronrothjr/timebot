import unittest
from timecard import Timecard
from datetime import date, time


class TestTimecard(unittest.TestCase):
    
    def setUp(self):
        self.timecard = Timecard(begin_date='20220220', days={
            'Sunday': {'0901': {'begin': '0901', 'end': '1600'}},
            'Monday': {'0902': {'begin': '0902', 'end': '1602'}},
            'Tuesday': {'0801': {'begin': '0801', 'end': '1501'}}
        })
    
    def test_can_instantuate_timecard(self):
        self.assertIsInstance(self.timecard, Timecard)
        self.assertIsInstance(self.timecard.begin_date, date)
        self.assertIsInstance(self.timecard.end_date, date)
        self.assertEqual(self.timecard.begin_date.day, 20)
        self.assertEqual(self.timecard.end_date.day, 26)
        self.assertIsInstance(self.timecard.days, dict)
        self.assertTrue(callable(self.timecard.add_day))
        self.assertTrue(callable(self.timecard.add_days))
        

    def test_can_add_days(self):
        self.assertEqual(self.timecard.days.get('Sunday').entries.get('0901').begin, time(9,1))
        entry = self.timecard.days.get('Tuesday').entries.get('0801')
        self.assertEqual(entry.end, time(15,1))