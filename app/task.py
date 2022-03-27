import os
from datetime import time
from utils import Utils


class Task:

    def __init__(self, *args):
        default_code = os.environ.get('DEFAULT_PROJECT_CODE')
        if len(args) == 1:
            task = args[0]
        else:
            task = {'entryid': args[0], 'dayid': args[1], 'begin': args[2], 'end': args[3], 'code': args[4]}
        self.entryid = task.get('entryid', 0)
        self.dayid = task.get('dayid', 0)
        self.begin = Utils.obj_format_time(task.get('begin'))
        self.end = Utils.obj_format_time(task.get('end'))
        self.code = task.get('code', default_code)

    def as_dict(self):
        items = {
            'entryid': self.entryid,
            'dayid': self.dayid,
            'begin': Utils.db_format_time(self.begin),
            'end': Utils.db_format_time(self.end),
            'code': self.code
        }
        return items
