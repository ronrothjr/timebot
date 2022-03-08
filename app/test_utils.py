import unittest, datetime, os
from timecard import Timecard
from utils import Utils


class TestUntils(unittest.TestCase):

    def test_get_tuples_from_data(self):
        today = datetime.datetime.now()
        begin_date = str((today - datetime.timedelta(days=today.weekday() + 1)).date())
        timecard_data = {
            'days': {
                'Monday': {
                    'dayid': 0, 'begin_date': begin_date, 'weekday': 'Monday', 'entries': {
                        0: {'dayid': 0, 'entryid': 0, 'begin': '0900', 'end': '1600', 'code': os.environ["DEFAULT_PROJECT_CODE"]}
                    }
                }
            }
        }
        new_timecard = Timecard(begin_date, timecard_data)
        timecard_dict = new_timecard.as_dict()
        column_tuple = Utils.schema_dict_to_tuple('timecard')
        self.assertEqual(column_tuple, [('Begin', 30, 'begin_date'), ('End', 30, 'end_date')])
        data_tuple = Utils.data_to_tuple('timecard', [timecard_dict])
        self.assertEqual(data_tuple[0][0], begin_date)


if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = '403001'
    unittest.main()