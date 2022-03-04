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
            project.add({'code': 'DRG-403009', 'show': 1})
            project.add({'code': 'DRG-403001', 'show': 1})
            project.add({'code': 'DRG-403005', 'show': 1})
            project.add({'code': 'DRG-413005', 'show': 1})
            project.add({'code': 'DRG-000099', 'show': 0})
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
    def remove_or_toggle_project_code(icon: str, code: str):
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        project_obj = project.get(code)
        if icon == 'close':
            project.remove(code)
        else:
            project.update(project_obj, {'show': 0 if icon == 'star' else 1})

    @staticmethod
    def switch_or_start_task(code: str):
        today = datetime.datetime.now()
        begin_date = str((today - datetime.timedelta(days=today.weekday() + 1)).date())
        weekday = Utils.weekdays[today.weekday() + 1]
        schema = Utils.get_schema()
        now = datetime.datetime.now().time()
        day = Service(Day, Sqlite3DB, schema)
        entry = Service(Entry, Sqlite3DB, schema)
        day_obj: Day = day.get({'begin_date': begin_date, 'weekday': weekday})[0]
        entries = entry.get({'dayid': day_obj.dayid})
        max_end_time = Utils.db_format_time(datetime.time(int(0), int(0)))
        now_str = Utils.db_format_time(now)
        for entry_obj in entries:
            in_progress = entry_obj.end is None
            code_change = entry_obj.code != code
            begin_str = Utils.db_format_time(entry_obj.begin)
            end_str = Utils.db_format_time(entry_obj.begin) if not in_progress else ''
            is_future = begin_str > now_str
            if begin_str < now_str and code_change and (in_progress or (not in_progress and end_str > now_str)):
                entry.update(entry_obj, {'end': now_str})
            if is_future:
                entry.remove(entry_obj.entryid)
            is_new_max = not in_progress and end_str > max_end_time and end_str < now_str
            max_end_time = end_str if is_new_max else (now_str if in_progress else max_end_time)
        if max_end_time < now_str and max_end_time != '0000':
            new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': max_end_time, 'end': now_str, 'code': 'DRG-000099'}
            entry.add(new_entry)
        entries = entry.get({'dayid': day_obj.dayid})
        last = None
        for entry_obj in entries:
            begin_str = Utils.db_format_time(entry_obj.begin)
            last_str = Utils.db_format_time(last.begin) if last else ''
            if not last or (last and begin_str > last_str):
                last = entry_obj
        if not last or (last.code != code and Utils.db_format_time(last.begin) != Utils.db_format_time(now)):
            new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': Utils.db_format_time(now), 'end': None, 'code': code}
            entry.add(new_entry)
            
        

if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"
    API.add_current_timecard()
