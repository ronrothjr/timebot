import os
from datetime import date, timedelta
from day import Day


class Timecard:
    
    default_entry = {'0900': {'begin': '0900', 'end': '1600', 'code': os.environ.get("DEFAULT_PROJECT_CODE", '')}}
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    
    def __init__(self, begin_date: str, days: dict):
        self.set_begin_date(date_str=begin_date)
        self.end_date = self.begin_date + timedelta(days=6)
        self.days = {}
        self.add_days(days)

    def as_dict(self):
        items = {'begin_date': self.begin_date, 'end_date': self.end_date, 'days': self.days}
        return items

    def set_begin_date(self, date_str: str):
        year = date_str[0:4]
        month = date_str[5:7]
        day = date_str[8:10]
        self.begin_date = date(int(year), int(month), int(day))

    def add_day(self, day: str, entries: dict):
        self.days[day] = Day(day, entries)

    def add_days(self, days: dict):
        for weekday in self.weekdays:
            entries = days.get(weekday)
            if not entries:
                entries = {} if weekday in ['Sunday', 'Saturday'] else self.default_entry
            self.add_day(weekday, entries)
