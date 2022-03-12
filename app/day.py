from task import Task


class Day:

    def __init__(self, *args):
        self.dayid = 0
        self.tasks = {}
        if len(args) == 1:
            day = args[0]
            self.dayid = day.get('dayid', 0)
            self.begin_date = day.get('begin_date')
            self.weekday = day.get('weekday')
            if day.get('tasks'):
                self.add_tasks(day.get('tasks'))
        else:
            self.begin_date = args[0]
            self.weekday = args[1]
            if len(args) > 2:
                self.add_entries(args[2])

    def add_tasks(self, tasks: dict):
        for entryid, task in tasks.items():
            if task:
                self.tasks[entryid] = Task(task)

    def as_dict(self):
        items = {'dayid': self.dayid, 'begin_date': str(self.begin_date), 'weekday': self.weekday, 'tasks': self.tasks_as_dict()}
        return items

    def tasks_as_dict(self):
        tasks_dict = {}
        for entryid, task in self.tasks.items():
            tasks_dict[entryid] = task.as_dict()
        return tasks_dict
