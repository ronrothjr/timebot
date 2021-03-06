import datetime, os
from threading import stack_size
from typing import List
from service import Service
from db import Sqlite3DB
from task import Task
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
        setting = Service(object_class=Setting, database=Sqlite3DB, schema_dict=schema, setup=True)
        settings = setting.get('default_project_code')
        if not settings:
            setting.add({'key': 'default_project_code', 'value': 'DRG-000099', 'options': '', 'title': 'Default Project Code', 'type': 'string', 'desc': 'The default code to assign new tasks in a timecard', 'section': 'Timecards'})
        settings = setting.get('unbilled_project_code')
        if not settings:
            setting.add({'key': 'unbilled_project_code', 'value': 'DRG-000099', 'options': '', 'title': 'Unbilled Project Code', 'type': 'string', 'desc': 'The code to assign to any unbilled tasks', 'section': 'Timecards'})
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
        config_records = Utils.data_to_dict(table_name='setting', dict_list=settings, exclude_undefined=True)
        for record in config_records:
            if record.get('options'):
                record['options'] = record['options'].split(',')
        API.data().save_records('config', config_records)

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
        if key == 'default_project_code':
            os.environ["DEFAULT_PROJECT_CODE"] = value
        if key == 'unbilled_project_code':
            os.environ["UNBILLED_PROJECT_CODE"] = value
        setting = Service(Setting, Sqlite3DB, schema)
        setting_obj = setting.get(key)
        setting.update(setting_obj, {'value': value})

    @staticmethod
    def add_current_timecard():
        today, now, begin_date, weekday, schema = API.get_now()
        project = Service(Project, Sqlite3DB, schema)
        timecard = Service(Timecard, Sqlite3DB, schema)
        day = Service(Day, Sqlite3DB, schema)
        task = Service(Task, Sqlite3DB, schema)
        projects = project.get()
        if not projects:
            project.add({'code': 'DRG-403009', 'desc': 'WorkScope Exp', 'show': 1})
            project.add({'code': 'DRG-413009', 'desc': 'WorkScope Cap', 'show': 0})
            project.add({'code': 'DRG-403001', 'desc': 'Back Office Mgmt', 'show': 1})
            project.add({'code': 'DRG-403005', 'desc': 'Vendor Master Exp', 'show': 1})
            project.add({'code': 'DRG-413005', 'desc': 'Vendor Master Cap', 'show': 1})
            project.add({'code': 'DRG-000099', 'desc': 'UAT', 'show': 0})
        timecards = timecard.get({'begin_date': begin_date})
        if not timecards:
            code = os.environ["DEFAULT_PROJECT_CODE"]
            new_timecard = Timecard(begin_date)
            new_timecard.add_days({})
            timecard_dict = new_timecard.as_dict()
            timecard.add(timecard_dict)
            for weekday, day_obj in timecard_dict.get('days').items():
                tasks = day_obj.get('tasks', {})
                new_day = day.add(begin_date, weekday, tasks)
                for new_task in tasks.values():
                    new_task['entryid'] = 0
                    new_task['dayid'] = new_day.dayid
                    task.add(new_task)

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
    def get_today(task_weekday=None, dayid: int=None, begin_date_orig: str=None):
        today, now, begin_date, weekday, schema = API.get_now()
        day = Service(Day, Sqlite3DB, schema)
        task = Service(Task, Sqlite3DB, schema)
        if dayid:
            day_obj: Day = day.get(dayid)
        else:
            query = {
                'begin_date': begin_date_orig if begin_date_orig else begin_date,
                'weekday': task_weekday if task_weekday else weekday
            }
            day_obj: Day = day.get(query)[0]
        tasks = sorted(task.get({'dayid': day_obj.dayid}), key=lambda i: i.begin)
        return now, task, day_obj, tasks

    @staticmethod
    def get_total(task_weekday: str=None, dayid: int=None, tasks: List[dict]=None):
        total = 0
        if not tasks:
            tasks = []
            if task_weekday or dayid:
                now, task, day_obj, day_tasks = API.get_today(task_weekday, dayid)
                tasks += [e.as_dict() for e in day_tasks]
            else:
                for weekday in Utils.weekdays:
                    now, task, day_obj, day_tasks = API.get_today(weekday, dayid)
                    tasks += [e.as_dict() for e in day_tasks]
            tasks = Utils.data_to_dict(table_name='task', dict_list=tasks)
        unbilled = os.environ["UNBILLED_PROJECT_CODE"]
        for task in tasks:
            if '-' not in task['total'] and task['code'] != unbilled:
                total += int(task['total'].split(':')[0]) * 60
                total += int(task['total'].split(':')[1])
        total_str = f'{str(int(total/60))}:{str(total%60).rjust(2,"0")}'
        return total_str

    @staticmethod
    def get_current_timecard():
        today, now, begin_date, weekday, schema = API.get_now()
        timecard: Timecard = Service(Timecard).get(begin_date)
        return timecard

    @staticmethod
    def switch_or_start_task(code: str='', weekday: str=None, begin: str=None, end: str=None,  begin_date: str=None, add_new_override: bool=False):
        info = API.get_last_task_info(code, weekday, begin_date, add_new_override)
        if info['is_today'] and not add_new_override:
            API.update_or_remove_tasks(info, code)
        if info['add_break']:
            API.add_break({
                'task': info['task'],
                'dayid': info['dayid'],
                'begin': info['last_end_str'],
                'end': info['now_str']
            })
        if add_new_override and info['last_task'] and not info['last_task'].end:
            info['task'].update(info['last_task'], {'end': info['last_end_str']})
        if info['add_new_to_end'] and not info['add_break']:
             info['task'].add({
                'entryid': 0,
                'dayid': info['dayid'],
                'begin': begin if begin else info['last_end_str'],
                'end': end if end else None,
                'code': code
            })
        elif info['add_new_now']:
            info['task'].add({
                'entryid': 0,
                'dayid': info['dayid'],
                'begin': begin if begin else info['now_str'],
                'end': end if end else None,
                'code': code
            })

    @staticmethod
    def get_last_task_info(code, weekday, begin_date, add_new_override: bool=False):
        t, n, b, w, s = API.get_now()
        is_today = weekday is None and begin_date is None or w == weekday and b == begin_date
        now, task, day, tasks = API.get_today(weekday, begin_date_orig=begin_date)
        now_str = Utils.db_format_time(now)
        last = API.get_last_task(weekday, day.dayid)
        last_begin_str = Utils.db_format_time(last.begin) if last and last.begin else ''
        last_end_str = Utils.db_format_time(last.end) if last and last.end else \
            (now_str if not last or not add_new_override or now_str > last_begin_str else Utils.db_format_add_time(last_begin_str, 1))
        has_break = last_end_str and last_end_str != now_str and last_begin_str != now_str
        has_break_code = code != '' and last_end_str and last_end_str < now_str
        is_new_task = code != '' and not last
        add_break = is_today and has_break_code
        is_code_changed = code != '' and last and last.code != code and last_begin_str != now_str
        is_same_after_break = has_break and code == last.code
        add_new_to_end = add_new_override or (not is_today and (not last or last and last.end))
        add_new_now = is_today and (is_new_task or is_code_changed or is_same_after_break)
        return {
            'is_today': is_today,
            'now_str': now_str,
            'dayid': day.dayid,
            'task': task,
            'tasks': tasks,
            'last_task': tasks[-1] if tasks else None,
            'last_end_str': last_end_str,
            'add_break': add_break,
            'add_new_to_end': add_new_to_end,
            'add_new_now': add_new_now,
            'add_new_override': add_new_override
        }

    @staticmethod
    def update_or_remove_tasks(info, code):
        for task in info['tasks']:
            in_progress = task.end is None
            code_change = code != '' and task.code != code
            begin_str = Utils.db_format_time(task.begin)
            end_str = Utils.db_format_time(task.end) if not in_progress else ''
            is_current = begin_str < info['now_str']
            is_task_end_request = is_current and in_progress
            is_task_to_end = not in_progress and end_str > info['now_str']
            is_current_code_change = is_current and code_change and is_task_to_end
            if is_task_end_request or is_current_code_change:
                info['task'].update(task, {'end': info['now_str']})
            is_future = begin_str > info['now_str']
            if is_future:
                info['task'].remove(task.entryid)
            in_progress = task.end is None
            begin_str = Utils.db_format_time(task.begin)
            end_str = Utils.db_format_time(task.end) if not in_progress else ''

    @staticmethod
    def add_break(info):
        unbilled_project_code = Service(Setting).get('unbilled_project_code')
        unbilled = unbilled_project_code.value if unbilled_project_code else os.environ.get("UNBILLED_PROJECT_CODE", '0000')
        info['task'].add({
            'entryid': 0,
            'dayid': info['dayid'],
            'begin': info['begin'],
            'end': info['end'],
            'code': unbilled
        })

    @staticmethod
    def get_last_task(weekday: str=None, dayid: int=None):
        now, task, day_obj, tasks = API.get_today(weekday, dayid)
        last = None
        for task_obj in tasks:
            begin_str = Utils.db_format_time(task_obj.begin)
            last_str = Utils.db_format_time(last.begin) if last else ''
            if not last or (last and begin_str > last_str):
                last = task_obj
        return last

    @staticmethod
    def split_task_error_check(original, code: str, new_begin: str=None, new_end: str=None,  weekday: str=None, begin_date=None):
        now, task, day_obj, tasks = API.get_today(weekday, begin_date_orig=begin_date)
        task_obj, task_dict, next_task = None, None, None
        for obj in tasks:
            obj_dict = obj.as_dict()
            if obj_dict['begin'] == original[0]:
                task_obj = obj
                task_dict = obj_dict
        if task_obj:
            for obj in tasks:
                obj_dict = obj.as_dict()
                if obj_dict['begin'] > task_dict['begin'] and (not next_task or next_task and obj_dict['begin'] < next_task['begin']):
                    next_task = obj_dict
        original_begin = str(original[0])
        begin = original[0]
        end = Utils.db_format_time(datetime.datetime.now().time()) if original[1] == '(active)' else original[1]
        end_after_original = new_end and end and new_end >= end
        if end_after_original:
            return f'Cannot end after the original task'
        return {
            'task': task,
            'tasks': tasks,
            'day_obj': day_obj,
            'begin': begin,
            'end': end,
            'task_obj': task_obj,
            'next_task': next_task
        }

    @staticmethod
    def split_task(original, code: str, new_begin: str=None, new_end: str=None,  weekday: str=None, begin_date=None):
        info = API.split_task_error_check(original, code, new_begin, new_end,  weekday, begin_date)
        time_diff = int(Utils.get_time_delta(info['begin'], info['end']).seconds / 60)
        begin = Utils.db_format_add_time(info['begin'], 1)
        if time_diff < 2:
            end = Utils.db_format_add_time(info['end'], 1)
            original[1] = end if original[1] != '(active)' else original[1]
        else:
            end = info['end']
        info['task'].update(info['task_obj'], {'begin': new_end if new_end else begin, 'end': None if original[1] == '(active)' else original[1]})
        end_after_next_begin = info['next_task'] and end and end != '(active)' and info['next_task']['begin'] != end
        if time_diff < 2 and end_after_next_begin:
            API.move_or_cleanup_next_tasks(info['task'], original, info['tasks'], end)
        info['task'].add({
            'entryid': 0,
            'dayid': info['day_obj'].dayid,
            'begin': original[0],
            'end': new_end if new_end else begin,
            'code': code
        })

    @staticmethod
    def update_task_error_check(original, begin: str, end: str, code: str, weekday=None, begin_date=None):
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
            return f'invalid value for {begin} or {end}'
        schema = Utils.get_schema()
        project = Service(Project, Sqlite3DB, schema)
        project_obj = project.get(code)
        has_valid_project_code = project_obj
        if not has_valid_project_code:
            return f'invalid project code: {code}'
        now, task, day_obj, tasks = API.get_today(weekday, begin_date_orig=begin_date)
        task_obj, task_dict, previous_task, previous_obj, next_task, next_obj = None, None, None, None, None, None
        for obj in tasks:
            obj_dict = obj.as_dict()
            if obj_dict['begin'] == original[0]:
                task_obj = obj
                task_dict = obj_dict
        if task_obj:
            for obj in tasks:
                obj_dict = obj.as_dict()
                if obj_dict['begin'] > task_dict['begin'] and (not next_task or next_task and obj_dict['begin'] < next_task['begin']):
                    next_task = obj_dict
                    next_obj = obj
                if obj_dict['begin'] < task_dict['begin'] and (not previous_task or previous_task and obj_dict['begin'] > previous_task['begin']):
                    previous_task = obj_dict
                    previous_obj = obj
        begin_before_begin = previous_task and begin < previous_task['begin']
        if begin_before_begin:
            return f'Cannot start before the previous task'
        # end_before_end = end and next_task and next_task['end'] and end > next_task['end']
        # if end_before_end:
        #     return f'Cannot end after the next task'
        return {
            'task': task,
            'tasks': tasks,
            'task_obj': task_obj,
            'next_task': next_task,
            'previous_obj': previous_obj,
            'previous_task': previous_task
        }

    @staticmethod
    def update_task(original, begin: str, end: str, code: str, weekday=None, begin_date=None):
        info = API.update_task_error_check(original, begin, end, code, weekday, begin_date)
        if isinstance(info, str):
            return info
        if info['task_obj']:
            begin_before_prev_end = info['previous_task'] and info['previous_task']['end'] != begin
            if begin_before_prev_end:
                begin_on_prev_begin = begin == info['previous_task']['begin']
                if begin_on_prev_begin:
                    info['task'].remove(info['previous_obj'].entryid)
                else:
                    info['task'].update(info['previous_obj'], {'end': begin})
            end_after_next_begin = info['next_task'] and end and info['next_task']['begin'] != end
            if end_after_next_begin:
                API.move_or_cleanup_next_tasks(info['task'], original, info['tasks'], end)
            info['task'].update(info['task_obj'], {'begin': begin, 'end': None if end == '' else end, 'code': code})

    @staticmethod
    def move_or_cleanup_next_tasks(task, original, tasks, end):
        time_diff = None
        for obj in tasks:
            obj_dict = obj.as_dict()
            if obj_dict['begin'] > original[0]:
                if not time_diff:
                    time_delta = Utils.get_time_delta(obj_dict['begin'], end)
                    time_diff = time_delta.seconds / 60
                if time_diff:
                    task.update_no_backup(obj, {
                        'begin': Utils.db_format_add_time(obj_dict['begin'], time_diff), 
                        'end': Utils.db_format_add_time(obj_dict['end'], time_diff)
                    })

    @staticmethod
    def remove_task(begin: str, end: str, code: str, weekday: str=None, begin_date=None):
        now, task, day_obj, tasks = API.get_today(weekday, begin_date_orig=begin_date)
        for task_obj in tasks:
            task_dict = task_obj.as_dict()
            if task_dict['begin'] == begin:
                task.remove(task_obj.entryid)
        for task_obj in tasks:
            task_dict = task_obj.as_dict()
            if end and task_dict['begin'] == end:
                task.update(task_obj, {'begin': begin})

    @staticmethod
    def resume_task():
        now, task, day_obj, tasks = API.get_today()
        last = API.get_last_task()
        if last:
            task.update(last, {'end': None})

if __name__ == '__main__':
    os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"
    API.add_current_timecard()
