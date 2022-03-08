import datetime

class Utils:

    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
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
    def get_schema():
        tables = {
            'project': {
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'id': True, 'dp': 30},
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
            'entry': {
                'dayid': {'name': 'dayid', 'type': 'INTEGER', 'dp': 10, 'ref': 'day(dayid)', 'trigger': 'CASCADE'},
                'begin': {'name': 'begin', 'display': 'Begin', 'type': 'TEXT', 'dp': 50},
                'end': {'name': 'end', 'display': 'End', 'type': 'TEXT', 'dp': 55},
                'total': {'name': 'total', 'display': 'Total', 'type': 'CALCULATED', 'dp': 50, 'calc': Utils.entry_total},
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'dp': 90, 'ref': 'project(code)', 'trigger': 'CASCADE'}
            }
        }
        return {'db_name': 'app.db', 'tables': tables}

    @staticmethod
    def entry_total(entry):
        begin = entry.get('begin')
        end = entry.get('end') if entry.get('end') else Utils.db_format_time(datetime.datetime.now().time())
        time_1 = datetime.datetime.strptime(f'{begin[0:2]}:{begin[-2:]}:00',"%H:%M:%S")
        time_2 = datetime.datetime.strptime(f'{end[0:2]}:{end[-2:]}:00',"%H:%M:%S")
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
    def obj_format_time(t: str):
        obj_time = None
        if t:
            time_str = t
            hour = int(time_str[0:2])
            minute = int(time_str[-2:])
            obj_time = datetime.time(hour, minute)
        return obj_time

    @staticmethod
    def db_format_time(t: datetime.time):
        if t:
            hour = str(t.hour).rjust(2, '0')
            minute = str(t.minute).rjust(2, '0')
            return f'{hour}{minute}'
        return None

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
    def data_to_dict(table_name: str, data: list):
        table = Utils.get_schema()['tables'][table_name]
        rows = []
        columns = [name for name, value in table.items() if 'display' in value]
        for row_data in data:
            dict_data = {}
            for name in columns:
                dict_data[name] = Utils.get_data_from_schema(name, table, row_data)
            rows.append(dict_data)
        return rows

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
        print(begin_date, weekday, code)
        
