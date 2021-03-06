from functools import partial
import datetime
from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivymd.uix.taptargetview import MDTapTargetView
from kivy.uix.scrollview import ScrollView
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import  FloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRoundFlatButton
from kivy.uix.behaviors import ButtonBehavior
from .orienter import Orienter
from .task_edit import TaskEdit
from project import Project
from timecard import Timecard


class MDBoxButton(ButtonBehavior, MDBoxLayout):
    pass


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass


class TimebotTasksScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotTasksScreen, self).__init__(**kw)
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.project_width = dp(400)
        self.project_height = dp(280)
        self.today_width = dp(360)
        self.task_width = dp(340)
        self.check_active_event = None
        self.orienter = Orienter()
        self.add_widget(self.orienter)
        self.task_edit = TaskEdit(self.task_edit_callback)
        self.load_task_entry()
        self.orienter.set_callback(self.orient)
        self.orienter.orient()
        # self.rotate()

    def refresh(self):
        self.load_task_entry()

    def load_task_entry(self):
       self.orienter.clear_widgets()
       self.get_today()
       self.add_project_box()
       self.add_heading()
       self.add_time_box()
       self.add_project_grid()
       self.show_project_grid()
       self.add_today()

    def orient(self, orienter):
        if orienter.orientation == 'vertical':
            self.project_box.size_hint_y = None
        else:
            self.project_box.size_hint_y = 1
        self.scroll_to_last()

    def on_enter(self):
        if hasattr(self, 'orienter'):
            self.show_project_grid()
            self.fill_task_grid()

    def rotate(self):
        rotation = Window.rotation
        def rotate(rotation, *args):
            Window.rotation = rotation
        Clock.schedule_once(partial(rotate, 90), .5)
        Clock.schedule_once(partial(rotate, rotation), 1)

    def get_today(self):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        self.weekday = weekday
        self.day = self.app.day.get({'begin_date': begin_date, 'weekday': weekday})[0]

    def add_project_box(self):
        self.project_box = MDGridLayout(cols=1, adaptive_size=True, size_hint=(.95, None), pos_hint=self.top_center)
        self.orienter.add_widget(self.project_box)

    def add_heading(self):
        widget_spacer = Widget(size_hint_y=None, height=dp(5))
        self.project_box.add_widget(widget_spacer)
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(1, None), padding=0, spacing=0, pos_hint=self.top_center)
        self.fill_heading()
        if hasattr(self, 'show_time_interval'):
            Clock.unschedule(self.show_time_interval)
        self.show_time_interval = Clock.schedule_interval(self.show_time, 0.1)
        self.project_box.add_widget(self.heading_box)
        widget_spacer = Widget(size_hint_y=None, height=dp(5))
        self.project_box.add_widget(widget_spacer)

    def fill_heading(self):
        self.heading_box.clear_widgets()
        weekday_label = MDLabel(adaptive_height=True, text=self.day.weekday, size_hint_x=None, width=dp(110), font_style="H6")
        timecard: Timecard = self.app.api.get_current_timecard()
        self.heading_box.add_widget(weekday_label)
        timecard_label = MDLabel(adaptive_height=True, size_hint=(1, None), text=f"Week: {timecard.begin_date} - {timecard.end_date}", halign='right', font_style="Body2", pos_hint={'center_y': .5})
        self.heading_box.add_widget(timecard_label)

    def add_time_box(self):
        self.time_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), padding=0, spacing=0, pos_hint=self.top_center)
        current_time = self.app.utils.am_pm_format(datetime.datetime.now().strftime("%H:%M"))
        current_time_label = MDLabel(text=current_time, size_hint=(1, None), height=dp(40), font_style="H3", halign="center")
        self.time_label = current_time_label
        self.time_box.add_widget(current_time_label)
        self.project_box.add_widget(self.time_box)
        
    def add_project_grid(self):
        project_label = MDLabel(size_hint=(1, None), height=dp(20), halign="center", text="Select a project to record a task", font_style="Body2", pos_hint={"center_x": .5})
        self.project_box.add_widget(project_label)
        self.project_scroller = ScrollView(bar_width = 0, size_hint = (0.9, None), height = dp(200), pos_hint = self.top_center)
        self.project_view = MDList(adaptive_height=True, spacing=dp(10), pos_hint=self.top_center)
        self.project_grid = MDGridLayout(cols=2, padding=dp(10), spacing=dp(20), adaptive_size=True, size_hint=(1, None), pos_hint=self.top_center)
        self.project_view.add_widget(self.project_grid)
        self.project_scroller.add_widget(self.project_view)
        self.project_box.add_widget(self.project_scroller)

    def show_project_grid(self):
        self.project_grid.clear_widgets()
        projects: List[Project] = sorted(self.app.project.get({'show': 1}), key=(lambda p: p.code))
        for project in projects:
            self.add_project_card(project)

    def add_project_card(self, project: Project):
        project_card = MD3Card(padding=0, radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(1, None), size=(dp(120), dp(80)), line_color=(1,1,1,1), on_release=self.released)
        project_layout = MDRelativeLayout(size=project_card.size, pos_hint=self.center_center)
        project_label = MDLabel(text=project.code, adaptive_width=True, font_style="H6", halign="center", size_hint=(1, None), pos_hint=self.center_center)
        project_desc_float = FloatLayout(pos_hint={'center_y': 0.22})
        project_desc_label = MDLabel(text=project.desc, adaptive_width=True, font_style="Overline", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        project_desc_float.add_widget(project_desc_label)
        project_layout.add_widget(project_label)
        project_layout.add_widget(project_desc_float)
        project_card.add_widget(project_layout)
        self.project_grid.add_widget(project_card)

    def released(self, instance):
        self.app.api.switch_or_start_task(instance.children[0].children[1].text)
        self.fill_task_grid()
        self.scroll_to_last()

    def add_today(self):
        self.weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, 1), width=self.today_width, spacing=dp(5), pos_hint=self.top_center)
        self.orienter.add_widget(self.weekday_box)
        self.fill_weekday_box()

    def load_new_day(self):
        add_new_timecard = self.weekday == 'Saturday'
        if add_new_timecard:
            self.app.api.add_current_timecard()
        self.refresh()

    def fill_weekday_box(self):
        self.weekday_box.clear_widgets()
        self.add_column_headers()
        self.add_task_grid()
        self.add_last_task_button()
        self.fill_task_grid()
        self.schedule_check_active_event()

    def schedule_check_active_event(self):
        if self.check_active_event:
            Clock.unschedule(self.check_active_event)
        self.check_active_event = Clock.schedule_interval(self.check_active, 1)

    def check_active(self, *args):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        is_same_day = self.weekday == weekday
        has_tasks = hasattr(self, 'task_view') and self.task_view.children
        if has_tasks:
            self.update_active_task(is_same_day)
        elif not is_same_day:
            self.load_new_day()

    def update_active_task(self, is_same_day: bool):
        last_task_row = self.task_view.children[0].children[0]
        task_row_labels = list(reversed([c for c in last_task_row.children if isinstance(c, MDLabel)]))
        is_last_task_active = self.tasks and task_row_labels and task_row_labels[1].text == '(active)'
        if is_last_task_active:
            last_task = self.tasks[-1]
            if not is_same_day:
                self.app.task.update(last_task, {'end': '2359'})
                self.load_new_day()
                self.app.api.switch_or_start_task(last_task.code, begin='0000')
            else:
                last_dict = self.app.utils.data_row_to_dict('task', last_task.as_dict())
                task_row_labels[2].text = last_dict['total']
        elif not is_same_day:
            self.load_new_day()

    def add_column_headers(self):
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        column_total = 20
        for column in task_column_data:
            column_total += column[1]
        position = 0
        x = float("{:.4f}".format(10 / column_total))
        position += 10
        self.task_column_box = MDBoxLayout(orientation='vertical', size_hint=(.95, None), height=dp(30), padding=0, spacing=0, pos_hint=self.top_center)
        task_column_layout = MDRelativeLayout(size=self.task_column_box.size, pos_hint=self.top_center)
        for task_column in task_column_data:
            width = task_column[1]
            x = float("{:.4f}".format(position / column_total))
            position += width
            task_label = MDLabel(adaptive_height=True, size_hint=(width / column_total, None), text=task_column[0], font_style="Body1", pos_hint={'x': x, 'center_y': 0.5})
            task_column_layout.add_widget(task_label)
        self.task_column_box.add_widget(task_column_layout)
        self.weekday_box.add_widget(self.task_column_box)

    def show_time(self, *args):
        self.time_label.text = self.app.utils.am_pm_format(datetime.datetime.now().strftime("%H:%M"))

    def add_task_grid(self):
        self.task_scroller = ScrollView(bar_width = 6, size_hint = (None, 1), width=self.task_width, pos_hint = self.top_center)
        self.task_view = MDList(spacing=dp(6), pos_hint=self.top_center)
        self.task_scroller.add_widget(self.task_view)
        self.weekday_box.add_widget(self.task_scroller)

    def add_last_task_button(self):
        self.last_task_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint_x=None, width=self.task_width, padding=0, spacing=0, pos_hint=self.top_center)
        self.weekday_box.add_widget(self.last_task_box)

    def fill_task_grid(self, *args):
        self.task_view.clear_widgets()
        self.last_task_box.clear_widgets()
        self.tasks = self.app.task.get({'dayid': self.day.dayid})
        if self.tasks:
            self.tasks = sorted(self.tasks, key = lambda i: i.begin)
            self.show_task_grid()
            self.show_last_task_button()
        else:
            self.show_empty_card()

    def show_task_grid(self):
        dict_task_rows = self.app.utils.data_to_dict('task', [task.as_dict() for task in self.tasks])
        for task in dict_task_rows:
            self.add_task_row(task)

    def show_empty_card(self):
        empty_card = MD3Card(padding=16, radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(.98, None), size=(dp(120), dp(80)), md_bg_color=gch('606060'), line_color=(1, 1, 1, 1))
        empty_layout = MDRelativeLayout(size=empty_card.size, pos_hint=self.center_center)
        empty_label = MDLabel(text="You have no tasks for today", adaptive_width=True, font_style="H6", halign="center", size_hint=(1, None), pos_hint=self.center_center)
        empty_layout.add_widget(empty_label)
        empty_card.add_widget(empty_layout)
        self.task_view.add_widget(empty_card)

    def add_task_row(self, task):
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        column_total = 20
        for column in task_column_data:
            column_total += column[1]
        position = 0
        x = float("{:.4f}".format(10 / column_total))
        position += 10
        task_row_box = MDBoxButton(orientation='horizontal', size_hint=(1, None), height=dp(50), md_bg_color=gch('242424'), radius=[dp(20), dp(7), dp(20), dp(7)], on_release=self.task_edit.edit_task)
        task_column_layout = MDRelativeLayout(size=task_row_box.size, pos_hint=self.top_center)
        for task_column in task_column_data:
            width = task_column[1]
            x = float("{:.4f}".format(position / column_total))
            position += width
            task_column_value = task[task_column[2]] if task[task_column[2]] else '(active)'
            task_label = MDLabel(adaptive_height=True, text=task_column_value, size_hint=(width / column_total, None), font_style="Body1", pos_hint={'x': x, 'center_y': 0.5})
            task_column_layout.add_widget(task_label)
        task_row_box.add_widget(task_column_layout)
        self.task_view.add_widget(task_row_box)

    def task_edit_callback(self, action, original, begin: str=None, end: str=None, code: str=None):
        if action == 'save':
            self.app.api.update_task(original, begin, end, code)
        elif action == 'split':
            new_begin = None if begin and original[0] == begin else begin
            new_end = None if end and original[1] == end else end
            self.app.api.split_task(original, code, new_begin=new_begin, new_end=new_end)
        elif action == 'delete':
            self.app.api.remove_task(*original)
        self.fill_task_grid()

    def show_last_task_button(self):
        last_task = self.app.api.get_last_task()
        widget_spacer = Widget(size_hint_y=None, height=dp(10))
        self.last_task_box.add_widget(widget_spacer)
        end_task = last_task and not last_task.end
        button_text = 'End Current' if end_task else 'Resume Last'
        button_action = self.end_task if end_task else self.continue_task
        end_task_button = MDRoundFlatButton(text=f"{button_text} Task", on_release=button_action, pos_hint=self.center_center, line_color=gch('ffffff'))
        self.last_task_box.add_widget(end_task_button)
        widget_spacer = Widget(size_hint_y=None, height=dp(20))
        self.last_task_box.add_widget(widget_spacer)

    def end_task(self, instance):
        self.app.api.switch_or_start_task()
        self.fill_task_grid()

    def continue_task(self, instance):
        self.app.api.resume_task()
        self.fill_task_grid()

    def scroll_to_last(self):
        is_scrollable = hasattr(self, 'task_scroller') and hasattr(self, 'task_view')
        has_tasks = hasattr(self, 'weekday_box') and hasattr(self, 'tasks') and self.tasks
        if is_scrollable and has_tasks and self.task_view.children:
            available = self.weekday_box.height - self.heading_box.height - self.task_column_box.height - self.last_task_box.height
            if self.task_view.height > available and self.task_scroller.height != 100:
                self.task_scroller.scroll_to(self.task_view.children[0])