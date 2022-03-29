import os
from functools import partial
import pydash as _
from kivy.metrics import dp
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivymd.toast import toast


class MDLabelButton(ButtonBehavior, MDLabel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TimebotUndoDialog(MDBoxLayout):
    pass


class TaskUndo():

    def __init__(self, manager):
        self.manager = manager
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.undo_dialog = None

    def open(self, action):
        undo_dialog = TimebotUndoDialog()
        self.undo_dialog = MDDialog(
            title=f'Select a restore point:',
            type="custom",
            content_cls=undo_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)]
        )
        self.undo_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.undo_dialog.open()
        self.add_data(action)
    
    def add_data(self, action, *args):
        self.backup_files = []
        for file in self.app.utils.get_backup_list(os.environ["TIMEBOT_ROOT"], 1000):
            self.backup_files.append(file)
        for file in self.backup_files:
            p = file['n'].split('.')
            date = f'{p[0][8:10]}/{p[0][10:12]}'
            time = f'{p[0][12:14]}:{p[0][14:16]}:{p[0][16:18]}'
            desc = p[2].replace("_", " ")if p[2] != "db" else ""
            file['text'] = f'{date} {time} - {desc}'
            file['selected'] = self.selected
            self.undo_dialog.content_cls.ids.undo_list.data.append(file)

    def selected(self, text):
        file = next((x for x in self.backup_files if x['text'] == text), None)
        toast(f'Restoring {file["text"]}')
        def restore(self):
            self.app.utils.restore_db(file, os.environ["TIMEBOT_ROOT"])
            self.manager.get_screen('TODAY').refresh()
            self.manager.get_screen('TIMECARDS').refresh()
            self.manager.get_screen('PROJECTS').refresh()
            self.undo_dialog.dismiss(force=True)
        Clock.schedule_once(partial(restore, self))
