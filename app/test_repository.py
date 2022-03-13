import unittest, os
from repository import Repository
from db import Sqlite3DB, DatabaseSchema
from task import Task
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils

os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"


class TestRepository(unittest.TestCase):

    def setUp(self) -> None:
        schema = DatabaseSchema(**Utils.get_schema())
        self.project = Repository[Project](Project, Sqlite3DB, schema)
        self.timecard = Repository[Timecard](Timecard, Sqlite3DB, schema)
        self.day = Repository[Day](Day, Sqlite3DB, schema)
        self.task = Repository[Task](Task, Sqlite3DB, schema)

    def tearDown(self) -> None:
        self.remove_db()

    def remove_db(self) -> None:
        try:
            os.remove('app.db')
        except:
            pass

    def test_can_instantiate_a_repository(self):
        self.assertIsInstance(self.task, Repository)
        self.assertIsInstance(self.task.db, Sqlite3DB)
        self.assertIsInstance(self.task.name, str)

    def test_repository_can_handle_timecard_data(self):
        self.project.add(Project({'code': 'DRG-403009', 'desc': 'Workscope Exp', 'show': 1}))
        self.project.add(Project({'code': 'DRG-403001', 'desc': 'Back Office Mgmt', 'show': 1}))
        self.project.add(Project({'code': 'DRG-403005', 'desc': 'Vendor Master Exp', 'show': 1}))
        self.project.add(Project({'code': 'DRG-413005', 'desc': 'Vendor Master Cap', 'show': 1}))
        self.project.add(Project({'code': 'DRG-000099', 'desc': 'UAT', 'show': 0}))
        self.timecard.add(Timecard('2022-02-20', {'days': {}}))
        day = Day('2022-02-20', 'Monday')
        day = self.day.add(day)
        task = Task(0, day.dayid, '0900', '1600', 'DRG-403009')
        task = self.task.add(task)
        self.task.update(task, {'begin': '0830'})
        tasks = self.task.get()
        self.assertEqual(len(tasks), 1, 'tasks should have only 1')
        task = tasks[0]
        self.assertEqual(Utils.db_format_time(task.end), '1600', '0830 entry should end at 4pm')
        self.day.update(day, {'weekday': 'Tuesday'})
        self.task.remove(task.entryid)
