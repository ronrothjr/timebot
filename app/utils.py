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
