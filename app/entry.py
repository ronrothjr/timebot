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
        self.set_begin_time(entry)
        self.set_end_time(entry)
        self.code = entry.get('code', default_code)

    def set_begin_time(self, entry: dict):
        if entry.get('begin'):
            begin_str = entry.get('begin')
            hour = begin_str[0:2]
            minute = begin_str[-2:]
            self.begin = time(int(hour), int(minute)) if entry.get('begin') else None
        else:
            self.begin = None

    def set_end_time(self, entry: dict):
        if entry.get('end'):
            end_str = entry.get('end')
            hour = end_str[0:2]
            minute = end_str[-2:]
            self.end = time(int(hour), int(minute)) if entry.get('end') else None
        else:
            self.end = None

    def as_dict(self):
        items = {'entryid': self.entryid, 'dayid': self.dayid, 'begin': Utils.db_format_time(self.begin), 'end': Utils.db_format_time(self.end), 'code': self.code}
        return items
