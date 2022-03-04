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
                'begin': {'name': 'begin', 'display': 'Begin', 'type': 'TEXT', 'dp': 30},
                'end': {'name': 'end', 'display': 'End', 'type': 'TEXT', 'dp': 30},
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'dp': 30, 'ref': 'project(code)', 'trigger': 'CASCADE'}
            }
        }
        return {'db_name': 'app.db', 'tables': tables}

    @staticmethod
    def schema_dict_to_tuple(table_name):
        columns = []
        schema = Utils.get_schema()
        for name, column in schema['tables'][table_name].items():
            if 'display' in column:
                columns.append((column['display'], column['dp']))
        return columns

    @staticmethod
    def db_format_time(t: datetime.datetime.time):
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
            tuple_data = tuple([row_data[name] for name in columns])
            rows.append(tuple_data)
        return rows

    def get_begin_date():
        today = datetime.datetime.now()
        begin_date = str((today - datetime.timedelta(days=today.weekday() + 1)).date())
        weekday = Utils.weekdays[today.weekday() + 1]
        return today, begin_date, weekday

    @staticmethod
    def switch_project_code_task(code: str):
        today, begin_date = Utils.get_begin_date()
        weekday = Utils.weekdays[today.weekday() + 1]
        print(begin_date, weekday, code)
        
