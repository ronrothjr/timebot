from datetime import date, timedelta
from hours import  Hours


class Timecard:
    begin_date = date(1, 1, 1)
    end_date = date(1, 1, 1)
    days = {}
    
    def __init__(self, begin_date: str, days: dict):
        self.set_begin_date(date_str=begin_date)
        self.end_date = self.begin_date + timedelta(days=6)
        self.add_days(days)

    def set_begin_date(self, date_str: str):
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        self.begin_date = date(int(year), int(month), int(day))

    def add_day(self, day: str, hours: dict):
        self.days[day] = Hours(hours)

    def add_days(self, days: dict):
        for day, hours in days.items():
            self.add_day(day, hours)
