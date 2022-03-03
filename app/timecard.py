import os
from datetime import date, timedelta
from day import Day


class Timecard:

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
                self.add_days(args[1].get('days'))

    def default_entry(self):
        return {0: {'begin': '0900', 'end': '1600', 'code': os.environ["DEFAULT_PROJECT_CODE"]}}

    def as_dict(self):
        items = {'begin_date': str(self.begin_date), 'end_date': str(self.end_date), 'days': self.days_as_dict()}
        return items

    def days_as_dict(self):
        days_dict = {}
        for weekday, day in self.days.items():
            days_dict[weekday] = day.as_dict()
        return days_dict

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
            entries_dict = {}
            day = days.get(weekday)
            if day:
                entries_dict = day.get('entries', {})
            else:
                entries_dict = {} if weekday in ['Sunday', 'Saturday'] else self.default_entry()
            self.add_day(weekday, entries_dict)
