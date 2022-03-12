import unittest, os
from service import Service
from db import Sqlite3DB, DatabaseSchema
from task import Task
from project import Project
from timecard import Timecard
from day import Day
from utils import Utils
from api import API


os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"


class TestRepository(unittest.TestCase):

    def setUp(self) -> None:
        schema = Utils.get_schema()
        self.project = Service(Project, Sqlite3DB, schema)
        self.timecard = Service(Timecard, Sqlite3DB, schema)
        self.day = Service(Day, Sqlite3DB, schema)
        self.task = Service(Task, Sqlite3DB, schema)

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
        self.project.add({'code': 'DRG-403009', 'show': 1})
        self.project.add({'code': 'DRG-403001', 'show': 1})
        self.project.add({'code': 'DRG-403005', 'show': 1})
        self.project.add({'code': 'DRG-413005', 'show': 1})
        self.project.add({'code': 'DRG-000099', 'show': 0})
        self.timecard.add('2022-02-20', {'days': {}})
        day = self.day.add('2022-02-20', 'Monday')
        task = self.task.add(0, day.dayid, '0900', '1600', 'DRG-403009')
        self.task.update(task, {'begin': '0830'})
        tasks = self.task.get()
        self.assertEqual(len(tasks), 1, 'tasks should have only 1')
        task = tasks[0]
        self.assertEqual(Utils.db_format_time(task.end), '1600', '0830 task should end at 4pm')
        self.day.update(day, {'weekday': 'Tuesday'})
        API.add_current_timecard()
        API.switch_or_start_task('DRG-403005')
