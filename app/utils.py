import os, datetime
from pathlib import Path
from tracemalloc import StatisticDiff
from db import Sqlite3DB, DatabaseSchema
from files import Files

class Utils:

    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    @staticmethod
    def backup_db(local_path: str=None, desc: str='') -> None:
        files = Files(local_path)
        local_path = local_path if local_path else files.local_path
        ts = files.get_timestamp()
        files.create_path('backup')
        files.create_path('backup', ts[:8])
        from_path = files.get_path(local_path, 'app.db')
        to_path = files.get_path(local_path, 'backup', ts[:8], f'app-{ts}.{desc}.db')
        files.copy_file(from_path, to_path)

    @staticmethod
    def get_backup_list(local_path: str=None, fetch_count: int=10):
        count = 0
        files = Files(local_path)
        local_path = local_path if local_path else files.local_path
        backup_path = files.get_path(local_path, 'backup')
        backup_list = []
        days = list(reversed(files.get_paths(backup_path)))
        for d in days:
            if count < fetch_count:
                backups = list(reversed([{'d': d, 'n': n, 'p': f'{files.get_path(d, n)}'} for n in files.get_files(d)]))
                remaining_to_fetch = fetch_count - count
                backup_list += backups[0:remaining_to_fetch]
                count = len(backup_list)
        return backup_list

    @staticmethod
    def restore_db(file: dict, local_path):
        files = Files(local_path)
        local_path = local_path if local_path else files.local_path
        from_path = files.get_path(file['d'], file['n'])
        to_path = files.get_path(local_path, 'app.db')
        files.copy_file(from_path, to_path)

    @staticmethod
    def remove_data(schema=None) -> None:
        schema = schema if schema else Utils.get_schema()
        db = Sqlite3DB(DatabaseSchema(**schema))
        for table in schema['tables'].keys():
            db.execute(f'delete from {table}')

    @staticmethod
    def remove_db() -> None:
        try:
            os.remove('app.db')
        except:
            pass
    
    @staticmethod
    def get_data(obj):
        data = {}
        obj_dict = obj if isinstance(obj, dict) else obj.as_dict()
        for k, v in obj_dict.items():
            if isinstance(v, (int, str)):
                data[k] = v if isinstance(v, int) else str(v)
            else:
                data[k] = Utils.get_data(v)
        return data

    @staticmethod
    def get_schema(folder: str=''):
        tables = {
            'project': {
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'id': True, 'dp': 30},
                'desc': {'name': 'desc', 'display': 'Desc', 'type': 'TEXT', 'dp': 80},
                'show': {'name': 'show', 'display': 'Show', 'type': 'INTEGER', 'dp': 30}
            },
            'timecard': {
                'begin_date': {'name': 'begin_date', 'display': 'Begin', 'type': 'TEXT', 'id': True, 'dp': 30},
                'end_date': {'name': 'end_date', 'display': 'End', 'type': 'TEXT', 'dp': 30}
            },
            'day': {
                'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'dp': 30, 'ref': 'timecard(begin_date)', 'trigger': 'CASCADE'},
                'weekday': {'name': 'weekday', 'display': 'Weekday', 'type': 'TEXT', 'dp': 30}
            },
            'task': {
                'entryid': {'name': 'entryid', 'type': 'INTEGER', 'id': True},
                'dayid': {'name': 'dayid', 'type': 'INTEGER', 'dp': 10, 'ref': 'day(dayid)', 'trigger': 'CASCADE'},
                'begin': {'name': 'begin', 'display': 'In', 'type': 'TEXT', 'dp': 60},
                'end': {'name': 'end', 'display': 'Out', 'type': 'TEXT', 'dp': 60},
                'total': {'name': 'total', 'display': 'Total', 'type': 'CALCULATED', 'dp': 40, 'calc': Utils.task_total},
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'dp': 80, 'ref': 'project(code)', 'trigger': 'CASCADE'}
            },
            'setting': {
                'key': {'name': 'key', 'display': 'Key', 'type': 'TEXT', 'id': True, 'dp': 80},
                'title': {'name': 'title', 'display': 'Title', 'type': 'TEXT', 'dp': 80},
                'type': {'name': 'type', 'display': 'Type', 'type': 'TEXT', 'dp': 40},
                'value': {'name': 'value', 'display': 'Value', 'type': 'TEXT', 'dp': 80},
                'options': {'name': 'options', 'display': 'Options', 'type': 'TEXT', 'dp': 80},
                'desc': {'name': 'desc', 'display': 'Desc', 'type': 'TEXT', 'dp': 300},
                'section': {'name': 'section', 'display': 'Section', 'type': 'TEXT', 'dp': 80},
            }
        }
        return {'db_name': os.path.join(folder if folder else os.environ.get('TIMEBOT_ROOT', ''), 'app.db'), 'tables': tables}

    @staticmethod
    def task_total(task):
        begin = task.get('begin')
        end = task.get('end') if task.get('end') else Utils.db_format_time(datetime.datetime.now().time())
        if end < begin:
            end = '2359'
        h, m = Utils.get_int_from_time_str(begin)
        time_1 = datetime.datetime(1, 1, 1, h, m)
        h, m = Utils.get_int_from_time_str(end)
        time_2 = datetime.datetime(1, 1, 1, h, m)
        diff: datetime.timedelta = time_2 - time_1
        minutes = int(diff.total_seconds() / 60)
        time_str = f'{int(minutes / 60)}:{str(minutes % 60).rjust(2, "0")}'
        return time_str

    @staticmethod
    def schema_dict_to_tuple(table_name):
        columns = []
        schema = Utils.get_schema()
        for name, column in schema['tables'][table_name].items():
            if 'display' in column:
                columns.append((column['display'], column['dp'], column['name']))
        return columns

    @staticmethod
    def get_int_from_time_str(t: str):
        h = int(t[0:2])
        if ':' in t:
            m = int(t[3:5])
            if 'PM' in t and h != 12:
                h += 12
            if 'AM' in t and h == 12:
                h -= 12
        else:
            m = int(t[-2:])
        return h, m

    @staticmethod
    def obj_format_time(t: str) -> datetime.time:
        obj_time = None
        if t:
            h, m = Utils.get_int_from_time_str(t)
            obj_time = datetime.time(h, m)
        return obj_time

    @staticmethod
    def obj_format_date(t: str) -> datetime.datetime:
        obj_date = None
        if t:
            h, m = Utils.get_int_from_time_str(t)
            obj_date = datetime.datetime(1, 1, 1, h, m)
        return obj_date

    @staticmethod
    def am_pm_format(t: str):
        str_time = None
        if t:
            h, m = Utils.get_int_from_time_str(t)
            obj_date = datetime.datetime(1, 1, 1, h, m)
            str_time = obj_date.strftime("%I:%M %p")
        return str_time

    @staticmethod
    def db_format_add_time(t: str, minutes: int):
        str_time = None
        if t:
            h, m = Utils.get_int_from_time_str(t)
            obj_date = datetime.datetime(1, 1, 1, h, m)
            time_delta = datetime.timedelta(minutes=minutes)
            obj_date += time_delta
            str_time = Utils.db_format_time(obj_date.time())
        return str_time

    @staticmethod
    def db_format_time(t: datetime.time) -> str:
        if t:
            hour = str(t.hour).rjust(2, '0')
            minute = str(t.minute).rjust(2, '0')
            return f'{hour}{minute}'
        return None

    @staticmethod
    def get_time_delta(t1: str, t2: str) -> datetime.timedelta:
        obj_time = 0
        if t1 and t2:
            obj_time = Utils.obj_format_date(t2) - Utils.obj_format_date(t1)
        return obj_time

    @staticmethod
    def data_to_tuple(table_name: str, data: list):
        table = Utils.get_schema()['tables'][table_name]
        rows = []
        columns = [name for name, value in table.items() if 'display' in value]
        for row_data in data:
            tuple_data = ([Utils.get_data_from_schema(name, table, row_data) for name in columns])
            rows.append(tuple_data)
        return rows

    @staticmethod
    def get_data_from_schema(column: str, table: dict, row_data: dict):
        column_definition = table.get(column)
        calc = column_definition.get('calc')
        result = calc(row_data) if calc else row_data.get(column)
        return result

    @staticmethod
    def data_to_list(table_name: str, data: list):
        table = Utils.get_schema()['tables'][table_name]
        rows = []
        columns = [name for name, value in table.items() if 'display' in value]
        for row_data in data:
            list_data = [Utils.get_data_from_schema(name, table, row_data) for name in columns]
            rows.append(list_data)
        return rows

    @staticmethod
    def data_to_dict(table_name: str, dict_list: list, exclude_undefined: bool=False):
        rows = []
        for row_data in dict_list:
            dict_data = Utils.data_row_to_dict(table_name, row_data, exclude_undefined)
            rows.append(dict_data)
        return rows

    @staticmethod
    def data_row_to_dict(table_name: str, row_data: dict, exclude_undefined: bool=False):
        dict_data = {}
        table = Utils.get_schema()['tables'][table_name]
        for column_name, value in table.items():
            if 'display' in value:
                 data_value = Utils.get_data_from_schema(column_name, table, row_data)
                 if not exclude_undefined or exclude_undefined and str(data_value) not in ['', 'None']:
                    dict_data[column_name] = data_value
        return dict_data

    @staticmethod
    def get_begin_date():
        today = datetime.datetime.now()
        days_from_sunday = 0 if today.weekday() == 6 else today.weekday() + 1
        sunday_date = (today - datetime.timedelta(days=days_from_sunday)).date()
        begin_date = str(sunday_date)
        weekday = Utils.weekdays[days_from_sunday]
        return today, begin_date, weekday

    @staticmethod
    def switch_project_code_task(code: str):
        today, begin_date = Utils.get_begin_date()
        weekday = Utils.weekdays[today.weekday() + 1]
        
