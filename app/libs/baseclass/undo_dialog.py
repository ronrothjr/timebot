import os, datetime
from functools import partial
import pydash as _
from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.taptargetview import MDTapTargetView
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.modalview import ModalView
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.list import OneLineListItem
from kivymd.toast import toast


class TimebotUndoDialog(MDBoxLayout):
    pass


class TaskUndo():

    def __init__(self):
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.undo_dialog = None

    def open(self, action):
        undo_dialog = TimebotUndoDialog()
        self.undo_dialog = MDDialog(
            title=f'Select {"a" if action == "redo" else "an"} {action} point:',
            type="custom",
            content_cls=undo_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)]
        )
        self.undo_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.undo_dialog.open()
        if action == 'undo':
            Clock.schedule_once(partial(self.add_undo_list, action), 0.5)
    
    def add_undo_list(self, action, *args):
        self.backup_files = []
        for file in self.app.utils.get_backup_list(os.environ["TIMEBOT_ROOT"], 20):
            self.backup_files.append(file)
        for file in self.backup_files:
            p = file['n'].split('.')
            file['day_time'] = f'{p[0][8:10]}/{p[0][10:12]} {p[0][12:14]}:{p[0][14:16]}:{p[0][16:18]}'
            file['desc'] = p[2].replace('_', ' ') if p[2] != 'db' else ''
            self.undo_dialog.content_cls.ids.undo_list.add_widget(OneLineListItem(
                text=f'{file["day_time"]} - {file["desc"]}',
                on_release=self.selected,
                secondary_font_style="Body2"
            ))

    def selected(self, *args):
        print(args)

    def close(self, *args):
        self.undo_dialog.dismiss(force=True)


