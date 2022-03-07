from functools import partial
from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRoundFlatButton, MDTextButton
from kivymd.uix.textfield import MDTextField
from service import Service
from project import Project
from day import Day
from entry import Entry
from utils import Utils
from api import API


class TimebotEditTaskDialog(MDBoxLayout):
    pass

class TimebotConfirmDeleteTaskDialog(MDBoxLayout):
    pass

class TimebotEntryScreen(MDScreen):

    def on_enter(self):
        self.clear_widgets()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}
        self.view = MDList(spacing=dp(10))
        self.show_project_grid()
        self.list_view = MDList(spacing=dp(10))
        self.show_today()
        self.view.add_widget(self.list_view)
        self.scroller.add_widget(self.view)
        self.add_widget(self.scroller)

    def show_project_grid(self):
        self.project_grid = MDGridLayout(cols=2, padding="10dp", spacing="20dp", adaptive_size=True, size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        projects: List[Project] = Service(Project).get({'show': 1})
        for project in projects:
            project_card = MD3Card(padding=16, radius=[15,], size_hint=(1, None), size=('120dp', "80dp"), line_color=(1, 1, 1, 1), on_release=self.released)
            project_layout = MDRelativeLayout(size=project_card.size, pos_hint={"center_x": .5, "center_y": .5})
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Caption", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
            project_layout.add_widget(project_label)
            project_card.add_widget(project_layout)
            self.project_grid.add_widget(project_card)
        self.view.add_widget(self.project_grid)

    def show_today(self):
        self.list_view.clear_widgets()
        today, begin_date, weekday = Utils.get_begin_date()
        day = Service(Day).get({'begin_date': begin_date, 'weekday': weekday})[0]
        entries = Service(Entry).get({'dayid': day.dayid})
        if not entries:
            self.show_empty_card()
        else:
            self.show_weekday(day, entries)

    def show_empty_card(self):
        empty_card = MD3Card(padding=16, radius=[15,], size_hint=(.98, None), size=('120dp', "80dp"), md_bg_color=gch('606060'), line_color=(1, 1, 1, 1))
        empty_layout = MDRelativeLayout(size=empty_card.size, pos_hint={"center_x": .5, "center_y": .5})
        empty_label = MDLabel(text="You have no tasks for today", adaptive_width=True, font_style="Caption", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        empty_layout.add_widget(empty_label)
        empty_card.add_widget(empty_layout)
        self.list_view.add_widget(empty_card)

    def show_weekday(self, day, entries):
        self.weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, None), width="330dp", spacing="5dp", pos_hint={"center_x": .5})
        entry_rows = entries if isinstance(entries, list) else [entries]
        weekday_label = MDLabel(adaptive_height=True, text=day.weekday, font_style="H6")
        self.weekday_box.add_widget(weekday_label)
        self.add_task_grid(day, entry_rows)
        self.add_last_task_button()
        self.list_view.add_widget(self.weekday_box)

    def add_task_grid(self, day, entry_rows):
        self.add_weekday_header(day)
        for entry in entry_rows:
            self.add_entry_row(entry)

    def add_weekday_header(self, day):
        entry_column_box = MDBoxLayout(orientation='horizontal', size_hint=(0, None), height="30dp", width="320dp", padding=0, spacing=0)
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for entry_column in entry_column_data:
            entry_label = MDLabel(text=entry_column[0], size_hint=(None, None), width=dp(entry_column[1]), pos_hint={"center_x": .5, "center_y": .5}, font_style="Body1")
            entry_column_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_delete)
        self.weekday_box.add_widget(entry_column_box)

    def add_entry_row(self, entry):
        entry_row_box = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height="40dp", width="320dp", padding=0, spacing=0, line_color=gch('ffffff'), radius="10dp")
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", on_release=self.edit_task, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        entry_rowdata = entry.as_dict()
        for entry_column in entry_column_data:
            entry_column_value = entry_rowdata[entry_column[2]] if entry_rowdata[entry_column[2]] else '(active)'
            entry_label = MDLabel(text=entry_column_value, size_hint=(None, None), width=dp(entry_column[1]), pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2")
            entry_row_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.confirm_delete_entry, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_delete)
        self.weekday_box.add_widget(entry_row_box)

    def add_last_task_button(self):
        last_entry = API.get_last_entry()
        widget_spacer = Widget(size_hint_y=None, height="10dp")
        self.weekday_box.add_widget(widget_spacer)
        end_task = last_entry and not last_entry.end
        button_text = 'End Current' if end_task else 'Resume Last'
        button_action = self.end_task if end_task else self.continue_task
        end_task_button = MDRoundFlatButton(text=f"{button_text} Task", on_release=button_action, pos_hint={"center_x": .5, "center_y": .5}, line_color=gch('ffffff'))
        self.weekday_box.add_widget(end_task_button)

    def edit_task(self, instance):
        labels = [c.text for c in instance.parent.children]
        app = App.get_running_app()
        edit_dialog = TimebotEditTaskDialog()
        self.custom_dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=edit_dialog,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    on_release=self.cancel_dialog
                ),
                MDFlatButton(
                    text="SAVE", text_color=app.theme_cls.primary_color,
                    on_release=self.save_task
                ),
            ],
        )
        self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
        self.custom_dialog.open()
        self.original_values = list(reversed(labels[1:4]))
        self.custom_dialog.content_cls.ids.begin.text = self.original_values[0]
        self.custom_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.original_values[1] 
        self.custom_dialog.content_cls.ids.code.text = self.original_values[2]

    def released(self, instance):
        API.switch_or_start_task(instance.children[0].children[0].text)
        self.show_today()

    def cancel_dialog(self, *args):
        self.custom_dialog.dismiss(force=True)

    def save_task(self, *args):
        begin = self.custom_dialog.content_cls.ids.begin.text
        end = self.custom_dialog.content_cls.ids.end.text
        code = self.custom_dialog.content_cls.ids.code.text
        error = API.update_task(self.original_values, begin, end, code)
        if error:
            self.custom_dialog.content_cls.ids.error.text = error
        else:
            self.custom_dialog.dismiss(force=True)
            self.show_today()

    def confirm_delete_entry(self, instance):
        labels = [c.text for c in instance.parent.children]
        self.remove_me = list(reversed(labels[1:4]))
        app = App.get_running_app()
        confirm_dialog = TimebotConfirmDeleteTaskDialog()
        self.custom_dialog = MDDialog(
            title="Delete Task",
            type="custom",
            content_cls=confirm_dialog,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    on_release=self.cancel_dialog
                ),
                MDFlatButton(
                    text="OK", text_color=app.theme_cls.primary_color,
                    on_release=self.delete_entry
                ),
            ],
        )
        self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {labels[3]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {labels[2]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {labels[1]}'
        self.custom_dialog.open()

    def delete_entry(self, instance):
        self.custom_dialog.dismiss(force=True)
        API.remove_task(*self.remove_me)
        self.show_today()

    def end_task(self, instance):
        API.switch_or_start_task()
        self.show_today()

    def continue_task(self, instance):
        API.resume_task()
        self.show_today()


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass