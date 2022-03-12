import unittest, os
from datetime import  time
from task import Task


os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"


class TestTask(unittest.TestCase):
    
    def setUp(self):
        self.task = Task({'begin': '0901', 'end': '1600'})

    def test_can_instanciate_task(self):
        self.assertIsInstance(self.task, Task)
        self.assertIsInstance(self.task.begin, time)
        self.assertEqual(self.task.begin, time(9,1))

