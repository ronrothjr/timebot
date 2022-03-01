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

    def get_schema():        
        tables = {
            'project': {
                'code': {'name': 'code', 'type': 'TEXT', 'id': True}
            },
            'timecard': {
                'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'id': True},
                'end_date': {'name': 'end_date', 'type': 'TEXT'}
            },
            'day': {
                'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'ref': 'timecard(begin_date)', 'trigger': 'CASCADE'},
                'weekday': {'name': 'weekday', 'type': 'TEXT'}
            },
            'entry': {
                'dayid': {'name': 'dayid', 'type': 'INTEGER', 'ref': 'day(dayid)', 'trigger': 'CASCADE'},
                'begin': {'name': 'begin', 'type': 'TEXT'},
                'end': {'name': 'end', 'type': 'TEXT'},
                'code': {'name': 'code', 'type': 'TEXT', 'ref': 'project(code)', 'trigger': 'CASCADE'}
            }
        }
        return {'db_name': 'app.db', 'tables': tables}
