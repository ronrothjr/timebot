
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from db import DB

os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"

KV = """
MDScreen:

    MDToolbar:
        title: 'Time Bot'
        pos_hint: {'top': 1}

    MDFloatingActionButtonSpeedDial:
        data: app.add_buttons
        rotation_root_button: True
"""


class Example(MDApp):
    add_buttons = {
        "Timecard": "file-table-box-multiple",
        "Project": "apps",
        "Entry": "clock-time-five-outline",
    }

    def build(self):
        self.create_db()
        return Builder.load_string(KV)

    def create_db(self):
        timebot_tables = {
            'timecard': {
                'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'id': True},
                'end_date': {'name': 'end_date', 'type': 'TEXT'}
            },
            'day': {
                'timecard_begin_date': {'name': 'timecard_begin_date', 'type': 'TEXT', 'ref': 'timecard(begin_date)', 'trigger': 'CASCADE'},
                'weekday': {'name': 'weekday', 'type': 'TEXT', 'id': True}
            },
            'project': {
                'code': {'name': 'code', 'type': 'TEXT', 'id': True}
            },
            'entry': {
                'day_weekday': {'name': 'day_weekday', 'type': 'TEXT', 'ref': 'day(weekday)', 'trigger': 'CASCADE'},
                'begin': {'name': 'begin', 'type': 'TEXT'},
                'end': {'name': 'end', 'type': 'TEXT'},
                'project_code': {'name': 'project_code', 'type': 'TEXT', 'ref': 'project(code)', 'trigger': 'CASCADE'}
            }
        }
        self.db = DB(db_name='app.db', tables=timebot_tables)


Example().run()
