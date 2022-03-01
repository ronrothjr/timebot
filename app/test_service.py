import unittest, os
from service import Service
from db import Sqlite3DB, DatabaseSchema
from entry import Entry
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils


class TestRepository(unittest.TestCase):

    def setUp(self) -> None:
        schema = Utils.get_schema()
        self.project = Service(Project, Sqlite3DB, schema)
        self.timecard = Service(Timecard, Sqlite3DB, schema)
        self.day = Service(Day, Sqlite3DB, schema)
        self.entry = Service(Entry, Sqlite3DB, schema)

    def tearDown(self) -> None:
        self.remove_db()

    def remove_db(self) -> None:
        try:
            os.remove('app.db')
        except:
            pass

    def test_can_instantiate_a_repository(self):
        self.assertIsInstance(self.project, Service)
        self.assertIs(self.project.object_class, Project)
        self.assertIsInstance(self.project.repository.db, Sqlite3DB)

    def test_repository_can_handle_timecard_data(self):
        self.project.add('DRG-403009')
        self.project.add('DRG-403001')
        self.project.add('DRG-403005')
        self.project.add('DRG-413005')
        self.timecard.add('2022-02-20', {})
        day = self.day.add('2022-02-20', 'Monday')
        entry = self.entry.add(0, day.dayid, '0900', '1600', 'DRG-403009')
        self.entry.update(entry, {'begin': '0830'})
        entries = self.entry.get()
        self.assertEqual(len(entries), 1, 'entries should have only 1')
        entry = entries[0]
        self.assertEqual(entry.db_format_time(entry.end), '1600', '0830 entry should end at 4pm')
        self.day.update(day, {'weekday': 'Tuesday'})
        self.entry.remove(entry.entryid)
