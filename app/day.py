from entry import Entry


class Day:

    def __init__(self, weekday: str, entries: dict):
        self.weekday = weekday
        self.entries = {}
        self.add_entries(entries)

    def add_entries(self, entries: dict):
        for begin, entry in entries.items():
            self.entries[begin] = Entry(entry)

    def as_dict(self):
        items = {'weekday': self.weekday, 'entries': self.entries}
        return items
