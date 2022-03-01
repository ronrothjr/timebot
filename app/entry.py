import os
from datetime import time


class Entry:

    def __init__(self, *args):
        default_code = os.environ.get('DEFAULT_PROJECT_CODE')
        if len(args) == 1:
            entry = args[0]
        else:
            entry = {'entryid': args[0], 'dayid': args[1], 'begin': args[2], 'end': args[3], 'code': args[4]}
        self.entryid = entry.get('entryid')
        self.dayid = entry.get('dayid')
        self.set_begin_time(entry)
        self.set_end_time(entry)
        self.code = entry.get('code', default_code)

    def set_begin_time(self, entry: dict):
        begin_str = entry.get('begin')
        hour = begin_str[0:2]
        minute = begin_str[-2:]
        self.begin = time(int(hour), int(minute))

    def set_end_time(self, entry: dict):
        end_str = entry.get('end')
        hour = end_str[0:2]
        minute = end_str[-2:]
        self.end = time(int(hour), int(minute))

    def db_format_time(self, t: time):
        hour = str(t.hour).rjust(2, '0')
        minute = str(t.minute).rjust(2, '0')
        return f'{hour}{minute}'

    def as_dict(self):
        items = {'entryid': self.entryid, 'dayid': self.dayid, 'begin': self.db_format_time(self.begin), 'end': self.db_format_time(self.end), 'code': self.code}
        return items
