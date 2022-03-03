from entry import Entry


class Day:

    def __init__(self, *args):
        self.dayid = 0
        self.entries = {}
        if len(args) == 1:
            day = args[0]
            self.dayid = day.get('dayid', 0)
            self.begin_date = day.get('begin_date')
            self.weekday = day.get('weekday')
            if day.get('entries'):
                self.add_entries(day.get('entries'))
        else:
            self.begin_date = args[0]
            self.weekday = args[1]
            if len(args) > 2:
                self.add_entries(args[2])

    def add_entries(self, entries: dict):
        for entryid, entry in entries.items():
            if entry:
                self.entries[entryid] = Entry(entry)

    def as_dict(self):
        items = {'dayid': self.dayid, 'begin_date': str(self.begin_date), 'weekday': self.weekday, 'entries': self.entries_as_dict()}
        return items

    def entries_as_dict(self):
        entries_dict = {}
        for entryid, entry in self.entries.items():
            entries_dict[entryid] = entry.as_dict()
        return entries_dict
