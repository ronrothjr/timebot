
import datetime
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
from timecard import Timecard
from day import Day
from entry import Entry
from utils import Utils
from api import API


class TimebotEditTaskDialog(MDBoxLayout):
    pass

class TimebotConfirmDeleteTaskDialog(MDBoxLayout):
    pass

class Reorienter(MDBoxLayout):

    def __init__(self, **kw):
        super(Reorienter, self).__init__(**kw)
        self.size = (0.9, 1)
        self.pos_hint = {"center_x": .5, "top": 1}
        self.spacing = dp(10)
        self.reorient()

    def on_size(self, *args):
        self.reorient()

    def reorient(self):
        if self.width > self.height:
            self.orientation = 'horizontal'
        else:
            self.orientation = 'vertical'
        if hasattr(self, 'callback'):
            self.callback(self)


class TimebotEntryScreen(MDScreen):

    def on_enter(self):
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        if not hasattr(self, 'reorienter'):
            self.clear_widgets()
            self.reorienter = Reorienter()
            self.add_widget(self.reorienter)
            self.reorienter.reorient()
            self.add_project_grid()
            self.add_today()
            self.reorienter.callback = self.reorient
            self.reorienter.reorient()
        else:
            self.show_project_grid()
            self.fill_task_grid()

    def reorient(self, reorienter):
        if reorienter.orientation == 'vertical':
            self.project_scroller.size_hint_y = None
            self.project_scroller.height = '230dp'
        else:
            self.project_scroller.size_hint_y = 1

    def add_project_grid(self):
        self.project_scroller = ScrollView(bar_width = 0, size_hint = (0.9, 1), pos_hint = self.top_center)
        self.project_view = MDList(adaptive_height=True, spacing=dp(10), pos_hint=self.top_center)
        project_label = MDLabel(size_hint=(1, None), height="20px", halign="center", text=f"Select a project to record a task", font_style="Body2", pos_hint={"center_x": .5})
        self.project_view.add_widget(project_label)
        self.project_grid = MDGridLayout(cols=2, padding="10dp", spacing="20dp", adaptive_size=True, size_hint=(1, None), pos_hint=self.top_center)
        self.project_view.add_widget(self.project_grid)
        self.project_scroller.add_widget(self.project_view)
        self.reorienter.add_widget(self.project_scroller)
        self.show_project_grid()

    def show_project_grid(self):
        self.project_grid.clear_widgets()
        projects: List[Project] = Service(Project).get({'show': 1})
        for project in projects:
            project_card = MD3Card(padding=16, radius=[15,], size_hint=(1, None), size=('120dp', "80dp"), line_color=(1, 1, 1, 1), on_release=self.released)
            project_layout = MDRelativeLayout(size=project_card.size, pos_hint=self.center_center)
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Body1", halign="center", size_hint=(1, None), pos_hint=self.center_center)
            project_layout.add_widget(project_label)
            project_card.add_widget(project_layout)
            self.project_grid.add_widget(project_card)

    def add_today(self):
        today, begin_date, weekday = Utils.get_begin_date()
        self.day = Service(Day).get({'begin_date': begin_date, 'weekday': weekday})[0]
        self.weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, 1), width="360dp", spacing="5dp", pos_hint=self.top_center)
        self.add_heading()
        self.add_column_headers()
        self.add_task_grid()
        self.add_last_task_button()
        self.reorienter.add_widget(self.weekday_box)
        self.fill_task_grid()
        # self.resize_task_scroller()
        if hasattr(self, 'show_event'):
            Clock.unschedule(self.show_event)
        self.show_event = Clock.schedule_interval(self.fill_task_grid, 60)

    def add_heading(self):
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint_x=None, width="340dp", padding="0dp", spacing="0dp", pos_hint=self.top_center)
        weekday_label = MDLabel(adaptive_height=True, text=self.day.weekday[0:3], size_hint_x=None, width="50dp", font_style="H6")
        timecard: Timecard = API.get_current_timecard()
        self.heading_box.add_widget(weekday_label)
        self.time_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint_x=None, width="90dp", padding="0dp", spacing="0dp")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_time_label = MDLabel(adaptive_height=True, text=current_time, size_hint_x=None, width="90dp", font_style="H6")
        self.time_label = current_time_label
        self.time_box.add_widget(current_time_label)
        self.heading_box.add_widget(self.time_box)
        timecard_label = MDLabel(adaptive_height=True, size_hint=(1, None), text=f"Week of: {timecard.begin_date} - {timecard.end_date}", font_style="Body2")
        self.heading_box.add_widget(timecard_label)
        if hasattr(self, 'show_time_interval'):
            Clock.unschedule(self.show_time_interval)
        self.show_time_interval = Clock.schedule_interval(self.show_time, 0.1)
        self.weekday_box.add_widget(self.heading_box)

    def add_column_headers(self):
        self.entry_column_box = MDBoxLayout(orientation='horizontal', size_hint=(0, None), height="30dp", width="330dp", padding=0, spacing=0)
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", pos_hint=self.center_center)
        self.entry_column_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for entry_column in entry_column_data:
            entry_label = MDLabel(text=entry_column[0], size_hint=(None, None), width=dp(entry_column[1]), pos_hint=self.center_center, font_style="Body1")
            self.entry_column_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", pos_hint=self.center_center)
        self.entry_column_box.add_widget(entry_delete)
        self.weekday_box.add_widget(self.entry_column_box)

    def show_time(self, *args):
        self.time_label.text = datetime.datetime.now().strftime("%H:%M:%S")

    def add_task_grid(self):
        self.task_scroller = ScrollView(bar_width = 5, size_hint = (1, 1), pos_hint = self.top_center)
        self.task_view = MDList(spacing=dp(10), pos_hint=self.top_center)
        self.task_scroller.add_widget(self.task_view)
        self.weekday_box.add_widget(self.task_scroller)

    def add_last_task_button(self):
        self.last_task_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint_x=None, width="340dp", padding="0dp", spacing="0dp", pos_hint=self.top_center)
        self.weekday_box.add_widget(self.last_task_box)

    def fill_task_grid(self, *args):
        self.task_view.clear_widgets()
        self.last_task_box.clear_widgets()
        self.entries = Service(Entry).get({'dayid': self.day.dayid})
        if self.entries:
            self.show_task_grid()
            self.show_last_task_button()
        else:
            self.show_empty_card()

    def show_task_grid(self):
        dict_entry_rows = Utils.data_to_dict('entry', [entry.as_dict() for entry in self.entries])
        for entry in dict_entry_rows:
            self.add_entry_row(entry)

    def show_empty_card(self):
        empty_card = MD3Card(padding=16, radius=[15,], size_hint=(.98, None), size=('120dp', "80dp"), md_bg_color=gch('606060'), line_color=(1, 1, 1, 1))
        empty_layout = MDRelativeLayout(size=empty_card.size, pos_hint=self.center_center)
        empty_label = MDLabel(text="You have no tasks for today", adaptive_width=True, font_style="Caption", halign="center", size_hint=(1, None), pos_hint=self.center_center)
        empty_layout.add_widget(empty_label)
        empty_card.add_widget(empty_layout)
        self.task_view.add_widget(empty_card)

    def add_entry_row(self, entry):
        entry_row_box = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height="40dp", width="320dp", padding=0, spacing=0, line_color=gch('ffffff'), radius="10dp", pos_hint=self.top_center)
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", on_release=self.edit_task, pos_hint=self.center_center)
        entry_row_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for entry_column in entry_column_data:
            entry_column_value = entry[entry_column[2]] if entry[entry_column[2]] else '(active)'
            entry_label = MDLabel(text=entry_column_value, size_hint=(None, None), width=dp(entry_column[1]), pos_hint=self.center_center, font_style="Body2")
            entry_row_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.confirm_delete_entry, pos_hint=self.center_center)
        entry_row_box.add_widget(entry_delete)
        self.task_view.add_widget(entry_row_box)

    def show_last_task_button(self):
        last_entry = API.get_last_entry()
        widget_spacer = Widget(size_hint_y=None, height="10dp")
        self.last_task_box.add_widget(widget_spacer)
        end_task = last_entry and not last_entry.end
        button_text = 'End Current' if end_task else 'Resume Last'
        button_action = self.end_task if end_task else self.continue_task
        end_task_button = MDRoundFlatButton(text=f"{button_text} Task", on_release=button_action, pos_hint=self.center_center, line_color=gch('ffffff'))
        self.last_task_box.add_widget(end_task_button)
        widget_spacer = Widget(size_hint_y=None, height="20dp")
        self.last_task_box.add_widget(widget_spacer)

    def resize_task_scroller(self):
        self.task_scroller.size_hint_y = None
        self.task_scroller.height = self.weekday_box.height - self.heading_box.height - self.entry_column_box.height - self.last_task_box.height

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
        self.original_values = [labels[4], labels[3], labels[1]]
        self.custom_dialog.content_cls.ids.begin.text = self.original_values[0]
        self.custom_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.original_values[1] 
        self.custom_dialog.content_cls.ids.code.text = self.original_values[2]

    def released(self, instance):
        API.switch_or_start_task(instance.children[0].children[0].text)
        self.fill_task_grid()

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
            self.fill_task_grid()

    def confirm_delete_entry(self, instance):
        labels = [c.text for c in instance.parent.children]
        self.remove_me = [labels[4], labels[3], labels[1]]
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
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {self.remove_me[0]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {self.remove_me[1]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {self.remove_me[2]}'
        self.custom_dialog.open()

    def delete_entry(self, instance):
        self.custom_dialog.dismiss(force=True)
        API.remove_task(*self.remove_me)
        self.fill_task_grid()

    def end_task(self, instance):
        API.switch_or_start_task()
        self.fill_task_grid()

    def continue_task(self, instance):
        API.resume_task()
        self.fill_task_grid()


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass