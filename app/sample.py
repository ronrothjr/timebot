import os, datetime
from service import Service
from db import Sqlite3DB
from entry import Entry
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils


class Sample:

    @staticmethod
    def add_data(default_project_code: str):
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        timecard = Service(Timecard, Sqlite3DB, schema)
        day = Service(Day, Sqlite3DB, schema)
        entry = Service(Entry, Sqlite3DB, schema)
        project.add('DRG-403009')
        project.add('DRG-403001')
        project.add('DRG-403005')
        project.add('DRG-413005')
        today = str(datetime.datetime.now().date())
        new_timecard = Timecard(today, {'Monday': {'begin': '0900', 'end': '1600', 'code': default_project_code}})
        data = new_timecard.as_dict()
        timecard.add(data)
        for weekday, entries in data.days.items():
            new_day = day.add(today, weekday, entries)
            for new_entry in entries.values():
                new_entry['entryid'] = 0
                new_entry['dayid'] = new_day.dayid
                entry.add(new_entry)

if __name__ == '__main__':
    Sample.add_data('DRG-403001')
