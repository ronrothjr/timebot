import unittest, os
from timecard import Timecard
from datetime import date, time
from utils import Utils


os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"

class TestTimecard(unittest.TestCase):

    def setUp(self):
        self.timecard = Timecard('2022-02-20', {
            'days': {
                'Sunday': {
                    'dayid': 1, 'weekday': 'Sunday', 'entries': {
                        1: {'dayid': 1, 'entryid': 1, 'begin': '0901', 'end': '1600'}
                    }
                },
                'Monday': {
                    'dayid': 2, 'weekday': 'Monday', 'entries': {
                        2: {'dayid': 2, 'entryid': 2, 'begin': '0902', 'end': '1602'}
                    }
                },
                'Tuesday': {
                    'dayid': 3, 'weekday': 'Monday', 'entries': {
                        3: {'dayid': 3, 'entryid': 3, 'begin': '0801', 'end': '1501'}
                    }
                }
            }
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
        self.assertEqual(self.timecard.days.get('Sunday').entries.get(1).begin, time(9,1))
        entry = self.timecard.days.get('Tuesday').entries.get(3)
        self.assertEqual(entry.end, time(15,1))
        data = Utils.get_data(self.timecard)
        self.assertEqual(data['begin_date'], '2022-02-20')
