import unittest, os
from repository import Repository
from db import Sqlite3DB, DatabaseSchema
from entry import Entry
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils


class TestRepository(unittest.TestCase):

    def setUp(self) -> None:
        schema = DatabaseSchema(**Utils.get_schema())
        self.project = Repository[Project](Project, Sqlite3DB, schema)
        self.timecard = Repository[Timecard](Timecard, Sqlite3DB, schema)
        self.day = Repository[Day](Day, Sqlite3DB, schema)
        self.entry = Repository[Entry](Entry, Sqlite3DB, schema)

    def tearDown(self) -> None:
        self.remove_db()

    def remove_db(self) -> None:
        try:
            os.remove('app.db')
        except:
            pass

    def test_can_instantiate_a_repository(self):
        self.assertIsInstance(self.entry, Repository)
        self.assertIsInstance(self.entry.db, Sqlite3DB)
        self.assertIsInstance(self.entry.name, str)

    def test_repository_can_handle_timecard_data(self):
        self.project.add(Project('DRG-403009'))
        self.project.add(Project('DRG-403001'))
        self.project.add(Project('DRG-403005'))
        self.project.add(Project('DRG-413005'))
        self.timecard.add(Timecard('2022-02-20', {}))
        day = Day('2022-02-20', 'Monday')
        day = self.day.add(day)
        entry = Entry(0, day.dayid, '0900', '1600', 'DRG-403009')
        entry = self.entry.add(entry)
        self.entry.update(entry, {'begin': '0830'})
        entries = self.entry.get()
        self.assertEqual(len(entries), 1, 'entries should have only 1')
        entry = entries[0]
        self.assertEqual(entry.db_format_time(entry.end), '1600', '0830 entry should end at 4pm')
        self.day.update(day, {'weekday': 'Tuesday'})
        self.entry.remove(entry.entryid)
