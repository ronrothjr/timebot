import datetime, os
from service import Service
from db import Sqlite3DB
from entry import Entry
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils


class API:

    @staticmethod
    def add_current_timecard():
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
        today = datetime.datetime.now()
        begin_date = str((today - datetime.timedelta(days=today.weekday() + 1)).date())
        timecards = timecard.get({'begin_date': begin_date})
        if not timecards:
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

    @staticmethod
    def switch_or_start_task(code: str):
        today = datetime.datetime.now()
        begin_date = str((today - datetime.timedelta(days=today.weekday() + 1)).date())
        weekday = Utils.weekdays[today.weekday() + 1]
        print(begin_date, weekday, code)
        schema = Utils.get_schema()
        now = datetime.datetime.now().time()
        day = Service(Day, Sqlite3DB, schema)
        entry = Service(Entry, Sqlite3DB, schema)
        day_obj: Day = day.get({'begin_date': begin_date, 'weekday': weekday})[0]
        entries = entry.get({'dayid': day_obj.dayid})
        for entry_obj in entries:
            if entry_obj.begin < now and (entry_obj.end is None or entry_obj.end > now):
                entry.update(entry_obj, {'end': Utils.db_format_time(now)})
        new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': Utils.db_format_time(now), 'end': None, 'code': code}
        added = entry.add(new_entry)
        print(f'addd {added.as_dict()}')
            
        

if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"
    API.add_current_timecard()
