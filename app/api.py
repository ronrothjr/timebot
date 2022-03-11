import datetime, os
from threading import stack_size
from service import Service
from db import Sqlite3DB
from entry import Entry
from setting import Setting
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils
from data import Data
from files import Files


class API:

    @staticmethod
    def get_now():
        today, begin_date, weekday = Utils.get_begin_date()
        now = today.time()
        schema = Utils.get_schema()
        return today, now, begin_date, weekday, schema

    @staticmethod
    def data():
        return Data(Files())

    @staticmethod
    def add_settings():
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
        settings = setting.get('default_project_code')
        if not settings:
            setting.add({'key': 'default_project_code', 'value': 'DRG-000099', 'options': '', 'title': 'Default Project Code', 'type': 'string', 'desc': 'The default code to assign new tasks in a timecard', 'section': 'Timecards'})
        settings = setting.get('cascade_delete')
        if not settings:
            setting.add({'key': 'cascade_delete', 'value': '0', 'options': '', 'title': 'Cascade Delete', 'type': 'bool', 'desc': 'Allow child tasks to be deleted when a project code or timecard is removed', 'section': 'Timecards'})
        settings = setting.get('version_tour')
        if not settings:
            setting.add({'key': 'version_tour', 'value': '0.0.0', 'options': '1.1.0,1.0.0,0.0.2,0.0.1,0.0.0', 'title': 'Version Tour', 'type': 'options', 'desc': 'Change to take the tour of changes for a specific release', 'section': 'About'})
        API.save_config()
        API.save_my_config()

    @staticmethod
    def save_config():
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
        settings = [s.as_dict() for s in setting.get()]
        config_records = Utils.data_to_dict(table_name='setting', data=settings, exclude_undefined=True)
        for record in config_records:
            if record.get('options'):
                record['options'] = record['options'].split(',')

    @staticmethod
    def save_my_config():
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
        settings = [s.as_dict() for s in setting.get()]
        defaults = {}
        for s in settings:
            defaults[s['section']] = defaults[s['section']] if s['section'] in defaults else {}
            defaults[s['section']][s['key']] = s['value']
        API.data().save_records('my_config', defaults)

    @staticmethod
    def get_setting(key: str) -> str:
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
        return setting.get(key)

    @staticmethod
    def set_setting(key: str, value: str) -> str:
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
        setting_obj = setting.get(key)
        setting.update(setting_obj, {'value': value})

    @staticmethod
    def add_current_timecard():
        today, now, begin_date, weekday, schema = API.get_now()
        setting = Service(Setting, Sqlite3DB, schema)
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
            project.add({'code': 'DRG-413009', 'show': 0})
        timecards = timecard.get({'begin_date': begin_date})
        if not timecards:
            code = API.get_setting('default_project_code')
            print(code.as_dict())
            timecard_data = {
                'days': {
                    'Monday': {
                        'dayid': 0, 'begin_date': begin_date, 'weekday': 'Monday', 'entries': {
                            0: {'dayid': 0, 'entryid': 0, 'begin': '0800', 'end': '1600', 'code': code.value if code else os.environ["DEFAULT_PROJECT_CODE"]}
                        }
                    }
                }
            }
            new_timecard = Timecard(begin_date, timecard_data)
            data = new_timecard.as_dict()
            print(data)
            timecard.add(data)
            for weekday, day_obj in data.get('days').items():
                entries = day_obj.get('entries', {})
                new_day = day.add(begin_date, weekday, entries)
                for new_entry in entries.values():
                    new_entry['entryid'] = 0
                    new_entry['dayid'] = new_day.dayid
                    print(new_entry)
                    entry.add(new_entry)

    @staticmethod
    def toggle_project_code(icon: str, code: str):
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        project_obj = project.get(code)
        project.update(project_obj, {'show': 0 if icon == 'star' else 1})

    @staticmethod
    def remove_project_code(code: str):
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        project.remove(code)

    @staticmethod
    def get_today(task_weekday=None):
        print(task_weekday)
        today, now, begin_date, weekday, schema = API.get_now()
        day = Service(Day, Sqlite3DB, schema)
        entry = Service(Entry, Sqlite3DB, schema)
        day_obj: Day = day.get({'begin_date': begin_date, 'weekday': task_weekday if task_weekday else weekday})[0]
        entries = entry.get({'dayid': day_obj.dayid})
        return now, entry, day_obj, entries

    @staticmethod
    def get_total(task_weekday: str=None):
        total = 0
        entries = []
        if task_weekday:
            now, entry, day_obj, day_entries = API.get_today(task_weekday)
            entries += [e.as_dict() for e in day_entries]
        else:
            for weekday in Utils.weekdays:
                now, entry, day_obj, day_entries = API.get_today(weekday)
                entries += [e.as_dict() for e in day_entries]
        tasks = Utils.data_to_dict(table_name='entry', data=entries)
        for task in tasks:
            hour_total = int(task['total'].split(':')[0]) * 60
            if hour_total > 0:
                total += hour_total
                total += int(task['total'].split(':')[1])
        total_str = f'{str(int(total/60))}:{str(total%60).rjust(2,"0")}'
        print(f'total: {total_str}')
        return total_str



    @staticmethod
    def get_current_timecard():
        today, now, begin_date, weekday, schema = API.get_now()
        timecard: Timecard = Service(Timecard).get(begin_date)
        return timecard

    @staticmethod
    def switch_or_start_task(code: str='', weekday: str=None):
        t, n, b, w, s = API.get_now()
        is_today = weekday is None or w == weekday
        now, entry, day_obj, entries = API.get_today(weekday)
        now_str = Utils.db_format_time(now)
        print([e.as_dict() for e in entries])
        print(day_obj.weekday)
        if is_today:
            API.update_or_remove_tasks(entries, entry, code, now_str)
        entries = entry.get({'dayid': day_obj.dayid})
        last = API.get_last_entry(weekday)
        last_begin_str = Utils.db_format_time(last.begin) if last and last.begin else ''
        last_end_str = Utils.db_format_time(last.end) if last and last.end else ''
        has_break = last_end_str and last_begin_str != now_str
        has_break_code = code != '' and last_end_str and last_end_str < now_str
        is_new_task = code != '' and not last
        if is_today and has_break_code:
            new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': last_end_str, 'end': now_str, 'code': 'DRG-000099'}
            entry.add(new_entry)
        is_code_changed = code != '' and last and last.code != code and last_begin_str != now_str
        is_same_after_break = has_break and code == last.code
        if not is_today:
            if last.end:
                new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': Utils.db_format_time(last.end), 'end': None, 'code': code}
                entry.add(new_entry)
        elif is_new_task or is_code_changed or is_same_after_break:
            new_entry = {'entryid': 0, 'dayid': day_obj.dayid, 'begin': now_str, 'end': None, 'code': code}
            entry.add(new_entry)

    @staticmethod
    def update_or_remove_tasks(entries, entry, code, now_str):
        for entry_obj in entries:
            in_progress = entry_obj.end is None
            code_change = code != '' and entry_obj.code != code
            begin_str = Utils.db_format_time(entry_obj.begin)
            end_str = Utils.db_format_time(entry_obj.end) if not in_progress else ''
            is_current = begin_str < now_str
            is_task_end_request = is_current and in_progress
            is_task_to_end = not in_progress and end_str > now_str
            is_current_code_change = is_current and code_change and is_task_to_end
            if is_task_end_request or is_current_code_change:
                entry.update(entry_obj, {'end': now_str})
            is_future = begin_str > now_str
            if is_future:
                entry.remove(entry_obj.entryid)
            in_progress = entry_obj.end is None
            begin_str = Utils.db_format_time(entry_obj.begin)
            end_str = Utils.db_format_time(entry_obj.end) if not in_progress else ''

    @staticmethod
    def get_last_entry(weekday: str=None):
        now, entry, day_obj, entries = API.get_today(weekday)
        last = None
        for entry_obj in entries:
            begin_str = Utils.db_format_time(entry_obj.begin)
            last_str = Utils.db_format_time(last.begin) if last else ''
            if not last or (last and begin_str > last_str):
                last = entry_obj
        return last

    @staticmethod
    def update_task(original, begin: str, end: str, code: str, weekday=None):
        print(begin, end, code, weekday)
        has_valid_time_lengths = len(begin) == 3 or len(begin) == 4
        if not has_valid_time_lengths:
            return f'invalid length for begin: {begin}'
        if len(begin) == 3:
            begin = '0' + begin
        has_valid_time_lengths = len(end) == 0 or len(end) == 3 or len(end) == 4
        if not has_valid_time_lengths:
            return f'invalid length for end: {end}'
        if len(end) == 3:
            end = '0' + end
        try:
            int(begin[0:2])
            int(begin[-2:])
        except:
            return f'int value failed for begin: {begin}'
        has_valid_time_values = int(begin[0:2]) >= 0 and int(begin[0:2]) < 24 and int(begin[-2:]) >= 0 and int(begin[-2:]) < 60
        if len(end) == 4:
            try:
                int(end[0:2])
                int(end[-2:])
            except:
                return f'int value failed for end: {end}'
            has_valid_time_values = has_valid_time_values and int(end[0:2]) >= 0 and int(end[0:2]) < 24 and int(end[-2:]) >= 0 and int(end[-2:]) < 60 and begin < end
        if not has_valid_time_values:
            return f'invalid time value for {begin} or {end}'
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        project_obj = project.get(code)
        has_valid_project_code = project_obj
        if not has_valid_project_code:
            return f'invalid project code: {code}'
        now, entry, day_obj, entries = API.get_today(weekday)
        previous_task = None
        task_to_update = None
        next_task = None
        for entry_obj in entries:
            entry_dict = entry_obj.as_dict()
            if task_to_update:
                next_task = entry_obj
            if entry_dict['begin'] == original[0]:
                task_to_update = entry_obj
            if not task_to_update:
                previous_task = entry_obj
        if task_to_update:
            if previous_task and Utils.db_format_time(previous_task.end) > begin:
                if Utils.db_format_time(previous_task.begin) >= begin:
                    print('deleting previous task')
                    begin = Utils.db_format_time(previous_task.begin)
                    entry.remove(previous_task.entryid)
                else:
                    print('updating previous task')
                    entry.update(previous_task, {'end': begin})
            if end and next_task and Utils.db_format_time(next_task.begin) < end:
                if Utils.db_format_time(next_task.end) >= end:
                    print('deleting next task')
                    end = Utils.db_format_time(previous_task.end)
                    entry.remove(next_task.entryid)
                else:
                    print('updating next task')
                    entry.update(next_task, {'begin': end})
            print('updating current task')
            entry.update(task_to_update, {'begin': begin, 'end': None if end == '' else end, 'code': code})

    @staticmethod
    def remove_task(begin: str, end: str, code: str, weekday: str=None):
        print(begin, end, code)
        now, entry, day_obj, entries = API.get_today(weekday)
        for entry_obj in entries:
            entry_dict = entry_obj.as_dict()
            if entry_dict['begin'] == begin:
                entry.remove(entry_obj.entryid)
        for entry_obj in entries:
            entry_dict = entry_obj.as_dict()
            if end and entry_dict['begin'] == end:
                entry.update(entry_obj, {'begin': begin})

    @staticmethod
    def resume_task():
        now, entry, day_obj, entries = API.get_today()
        last = API.get_last_entry()
        if last:
            entry.update(last, {'end': None})

if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"
    API.add_current_timecard()
