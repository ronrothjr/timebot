
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from service import Service
from project import Project
from timecard import Timecard
from day import Day
from entry import Entry

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
        "Timecards": "file-table-box-multiple",
        "Project": "apps",
        "Entry": "clock-time-five-outline",
    }

    def build(self):
        self.services()
        return Builder.load_string(KV)

    def services(self):
        self.project = Service(Project)
        self.timecard = Service(Timecard)
        self.day = Service(Day)
        self.entry = Service(Entry)


Example().run()
