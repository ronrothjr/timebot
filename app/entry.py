import os
from datetime import time


class Entry:
    begin = time(9)
    end = time(4)
    code = ''

    def __init__(self, entry: dict):
        self.set_begin_time(entry)
        self.set_end_time(entry)
        self.code = entry.get('code', os.environ.get('DEFAULT_PROJECT_CODE'))

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

    def as_dict(self):
        items = {'begin': self.begin, 'end': self.end, 'code': self.code}
        return items
