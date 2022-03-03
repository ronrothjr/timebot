import datetime, os
from service import Service
from db import Sqlite3DB
from entry import Entry
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils


class Sample:

    @staticmethod
    def add_data():
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        timecard = Service(Timecard, Sqlite3DB, schema)
        day = Service(Day, Sqlite3DB, schema)
        entry = Service(Entry, Sqlite3DB, schema)
        projects = project.get()
        if not projects:
            project.add('DRG-403009')
            project.add('DRG-403001')
            project.add('DRG-403005')
            project.add('DRG-413005')
        timecards = timecard.get()
        if not timecards:
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
            data = new_timecard.as_dict()
            timecard.add(data)
            for weekday, day_obj in data.get('days').items():
                entries = day_obj.get('entries', {})
                new_day = day.add(begin_date, weekday, entries)
                for new_entry in entries.values():
                    new_entry['entryid'] = 0
                    new_entry['dayid'] = new_day.dayid
                    entry.add(new_entry)

if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"
    Sample.add_data()
