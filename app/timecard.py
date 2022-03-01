import os
from datetime import date, timedelta
from day import Day


class Timecard:
    
    default_entry = {'0900': {'begin': '0900', 'end': '1600', 'code': os.environ.get("DEFAULT_PROJECT_CODE", '')}}
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    
    def __init__(self, *args):
        self.days = {}
        if len(args) == 1:
            timecard = args[0]
            self.set_begin_date(date_str=timecard.get('begin_date'))
            self.end_date = self.get_date(date_str=timecard.get('end_date'))
            if timecard.get('days'):
                self.add_days(timecard.get('days'))
        else:
            self.set_begin_date(date_str=args[0])
            self.end_date = self.begin_date + timedelta(days=6)
            if len(args) > 1:
                self.add_days(args[1])

    def as_dict(self):
        items = {'begin_date': self.begin_date, 'end_date': self.end_date, 'days': self.days}
        return items

    def get_date(self, date_str: str):
        year = date_str[0:4]
        month = date_str[5:7]
        day = date_str[8:10]
        return date(int(year), int(month), int(day))

    def set_begin_date(self, date_str: str):
        self.begin_date = self.get_date(date_str)

    def add_day(self, weekday: str, entries: dict):
        self.days[weekday] = Day(self.begin_date, weekday, entries)

    def add_days(self, days: dict):
        for weekday in self.weekdays:
            entries = days.get(weekday)
            if not entries:
                entries = {} if weekday in ['Sunday', 'Saturday'] else self.default_entry
            self.add_day(weekday, entries)
