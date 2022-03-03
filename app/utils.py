from kivy.metrics import dp
from timecard import Timecard
from day import Day
from entry import Entry

class Utils:
    
    @staticmethod
    def get_data(obj):
        data = {}
        obj_dict = obj if isinstance(obj, dict) else obj.as_dict()
        for k, v in obj_dict.items():
            if isinstance(v, (dict, Timecard, Day, Entry)):
                data[k] = Utils.get_data(v)
            else:
                data[k] = v if isinstance(v, int) else str(v)
        return data

    @staticmethod
    def get_schema():        
        tables = {
            'project': {
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'id': True, 'dp': 70}
            },
            'timecard': {
                'begin_date': {'name': 'begin_date', 'display': 'Begin', 'type': 'TEXT', 'id': True, 'dp': 70},
                'end_date': {'name': 'end_date', 'display': 'End', 'type': 'TEXT', 'dp': 70}
            },
            'day': {
                'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'dp': 70, 'ref': 'timecard(begin_date)', 'trigger': 'CASCADE'},
                'weekday': {'name': 'weekday', 'display': 'Weekday', 'type': 'TEXT', 'dp': 70}
            },
            'entry': {
                'dayid': {'name': 'dayid', 'type': 'INTEGER', 'dp': 30, 'ref': 'day(dayid)', 'trigger': 'CASCADE'},
                'begin': {'name': 'begin', 'display': 'Begin', 'type': 'TEXT', 'dp': 70},
                'end': {'name': 'end', 'display': 'End', 'type': 'TEXT', 'dp': 70},
                'code': {'name': 'code', 'display': 'Code', 'type': 'TEXT', 'dp': 70, 'ref': 'project(code)', 'trigger': 'CASCADE'}
            }
        }
        return {'db_name': 'app.db', 'tables': tables}

    @staticmethod
    def schema_dict_to_tuple(table_name):
        columns = []
        schema = Utils.get_schema()
        for name, column in schema['tables'][table_name].items():
            if column['display']:
                columns.append((column['display'], column['dp']))
        return columns

    @staticmethod
    def data_to_tuple(table_name: str, data: list):
        table = Utils.get_schema()['tables'][table_name]
        rows = []
        columns = [name for name, value in table.items() if value['display']]
        for row_data in data:
            rows.append(tuple([row_data[name] for name in columns]))
        return rows
