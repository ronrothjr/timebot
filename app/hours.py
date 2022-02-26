from entry import Entry


class Hours:
    entries = {}

    def __init__(self, entries: dict):
        self.add_entries(entries)

    def add_entries(self, entries: dict):
        for hour, entry in entries.items():
            self.entries[hour] = Entry(entry)
