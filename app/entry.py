import os
from datetime import time
from utils import Utils


class Entry:

    def __init__(self, *args):
        default_code = os.environ.get('DEFAULT_PROJECT_CODE')
        if len(args) == 1:
            entry = args[0]
        else:
            entry = {'entryid': args[0], 'dayid': args[1], 'begin': args[2], 'end': args[3], 'code': args[4]}
        self.entryid = entry.get('entryid', 0)
        self.dayid = entry.get('dayid', 0)
        self.begin = Utils.obj_format_time(entry.get('begin'))
        self.end = Utils.obj_format_time(entry.get('end'))
        self.code = entry.get('code', default_code)

    def as_dict(self):
        items = {'entryid': self.entryid, 'dayid': self.dayid, 'begin': Utils.db_format_time(self.begin), 'end': Utils.db_format_time(self.end), 'code': self.code}
        return items
