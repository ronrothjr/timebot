import os, datetime
from functools import partial
from typing import List
from kivy.utils import get_color_from_hex as gch
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import FloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.modalview import ModalView
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.list import OneLineListItem
from .orienter import Orienter
from .task_edit import TaskEdit


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass


class MDBoxButton(ButtonBehavior, MDBoxLayout):
    pass


class MDFloatButton(ButtonBehavior, FloatLayout):
    pass


class TimebotTimecardsScreen(MDScreen):

    top_center = {"center_x": .5, "top": 1}
    mid_center = {"center_x": .5, "top": .9}
    center_center = {"center_x": .5, "center_y": .5}
    top_left = {"left": 1, "top": 1}
    today_width = dp(360)
    task_width = dp(360)
    weekday_width = dp(340)
    heading_height = dp(35)
    header_height = dp(30)
    task_height = dp(50)

    def __init__(self, **kw):
        super(TimebotTimecardsScreen, self).__init__(**kw)
        self.date = datetime.datetime.now().date()
        self.app = App.get_running_app()
        self.weekday = None
        self.today = self.app.utils.get_begin_date()
        self.mode = 'vertical'
        self.task_edit = TaskEdit(self.task_edit_callback)
        self.orienter = Orienter()
        self.add_widget(self.orienter)
        self.orienter.orient()
        self.orienter.set_callback(self.orient)
        self.check_active_event = None
        self.custom_dialog = None
        self.timesheets_modal_open = False
        self.timesheets_modal = self.add_timesheets_modal()
        Clock.schedule_once(self.load_current_timesheet, 2)

    def refresh(self):
        self.load_current_timesheet()

    def orient(self, orienter):
        self.mode = orienter.orientation
        self.load_timesheet_data()

    def on_enter(self):
        if self.today[2]:
            self.refresh_totals_and_tasks(self.today[2])

    def schedule_check_active_event(self):
        if self.check_active_event:
            Clock.unschedule(self.check_active_event)
        self.check_active_event = Clock.schedule_interval(self.check_active, 1)

    def check_active(self, *args):
        if self.today[2]:
            self.update_active_task_and_totals()
            self.set_hours()

    def update_active_task_and_totals(self):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        date = today.date()
        is_same_date = self.date == date
        self.date = date
        if not is_same_date:
            self.today = self.app.utils.get_begin_date()
            Clock.schedule_once(partial(self.load_new_timecard, begin_date), 1)
            Clock.schedule_once(self.set_hours, 1)
            return
        is_same_day = self.today[2] == weekday
        if self.mode == 'vertical':
            weekday_box = self.weekdays[self.today[2]]
        else:
            weekday_box = self.weekday_task_layout
        last_task_row = weekday_box.children[1].children[0] if len(weekday_box.children) > 1 and weekday_box.children[1].children else None
        task_row_labels = list(reversed([c for c in last_task_row.children if isinstance(c, MDLabel)])) if last_task_row else []
        day = next((d for d in self.days if d.weekday == weekday), None)
        tasks = self.tasks.get(day.dayid) if day else []
        dict_tasks = self.app.utils.data_to_dict('task', [t.as_dict() for t in tasks])
        self.totals[weekday].text = f'{self.app.api.get_total(tasks=dict_tasks)}' if tasks else '0:00'
        is_last_task_active = tasks and task_row_labels and task_row_labels[1].text == '(active)'
        if is_last_task_active:
            last_task = tasks[-1]
            if not is_same_day:
                last_task.end = datetime.datetime.time(23, 59)
            last_dict = self.app.utils.data_row_to_dict('task', last_task.as_dict())
            task_row_labels[2].text = last_dict['total']

    def refresh_totals_and_tasks(self, weekday):
        day = next((d for d in self.days if d.weekday == weekday), None)
        self.tasks[day.dayid] = self.app.task.get({'dayid': day.dayid})
        self.set_hours()
        self.expand_weekday(weekday, keep_expanded_state=True)

    def add_timesheets_modal(self):
        modal = ModalView(size_hint=(None, .6), width=dp(300), auto_dismiss=True, pos_hint=self.mid_center)
        view = ScrollView()
        timecard_list = MDSelectionList(spacing=dp(12))
        for timecard in list(reversed(self.app.timecard.get())):
            timecard_list.add_widget(OneLineListItem(
                text=f"Week of: {timecard.begin_date} - {timecard.end_date}",
                _no_ripple_effect=True,
                on_release=self.selected_timecard
            ))
        view.add_widget(timecard_list)
        modal.add_widget(view)
        return modal

    def selected_timecard(self, instance):
        begin_date = instance.text.split(': ')[1].split(' - ')[0]
        today = self.app.utils.get_begin_date()
        self.today = (self.today[0], begin_date, today[2] if self.today[1] == begin_date else None)
        self.timesheets_modal.dismiss()
        Clock.schedule_once(partial(self.load_new_timecard, begin_date))

    def load_new_timecard(self, begin_date, event=None):
        self.get_timecard_data(begin_date)
        self.load_timesheet_data()
        self.set_hours()

    def get_timecard_data(self, begin_date: str):
        self.timecard = self.app.timecard.get(begin_date)
        self.days = self.app.day.get({'begin_date': self.timecard.begin_date})
        dayids = [day.dayid for day in self.days]
        tasks = self.app.task.get({'dayid': dayids})
        self.tasks = {}
        for dayid in dayids:
            self.tasks[dayid] = list(filter(lambda t: t.dayid == dayid, tasks))

    def load_current_timesheet(self, *args):
        self.orienter.clear_widgets()
        self.get_timecard_data(self.today[1])
        self.load_timesheet_data()
        self.schedule_check_active_event()

    def load_timesheet_data(self):
        self.orienter.clear_widgets()
        self.add_timesheet_box()
        self.add_horizontal_task_view()
        self.add_heading()
        self.add_timecard_selector()
        self.add_hours_label()
        self.add_column_headers()
        self.add_weekdays_box()
        self.add_weekday_task_scroller()
        self.show_weekdays()

    def set_hours(self, tasks: List[dict]=None):
        tasks = []
        for d in self.tasks.values():
            for t in d:
                tasks.append(t.as_dict())
        dict_tasks = self.app.utils.data_to_dict('task', tasks)
        self.heading_info_box.children[0].text = f'{self.app.api.get_total(tasks=dict_tasks)}'

    def add_timesheet_box(self):
        self.timesheet_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, 1), width=self.today_width, padding=0, spacing=0, pos_hint=self.top_center)
        self.orienter.add_widget(self.timesheet_box)

    def add_horizontal_task_view(self):
        if self.mode == 'horizontal':
            self.weekday_task_layout = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, 1), width=self.task_width, pos_hint=self.top_left)
            self.orienter.add_widget(self.weekday_task_layout)

    def add_heading(self):
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, None), width=self.task_width, padding=0, spacing=0, pos_hint=self.top_center)
        self.heading_info_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(None, None), width=self.task_width, height=self.heading_height, padding=[dp(10), 0, 0, 0], spacing=0, pos_hint=self.top_center)
        self.heading_box.add_widget(self.heading_info_box)
        self.timesheet_box.add_widget(self.heading_box)

    def add_timecard_selector(self):
        timecard_selector = MDCard(padding=0, radius=[dp(7), dp(7), dp(7), dp(7)], size_hint=(None, None), width=dp(230), height=dp(30), on_release=self.choose_timesheet, line_color=(1,1,1,1))
        timecard_layout = MDRelativeLayout(size=timecard_selector.size, pos_hint=self.center_center)
        timecard_label = MDLabel(adaptive_height=True, text=f"Week of: {self.timecard.begin_date} - {self.timecard.end_date}", size_hint=(None, None), width=dp(200), height=dp(30), pos_hint={"center_x": .45, "center_y": .5}, font_style="Body2")
        timecard_layout.add_widget(timecard_label)
        select_icon = MDIconButton(icon='chevron-down', user_font_size="20sp", pos_hint={"center_x": .95, "center_y": .5})
        timecard_layout.add_widget(select_icon)
        timecard_selector.add_widget(timecard_layout)
        self.heading_info_box.add_widget(timecard_selector)

    def choose_timesheet(self, instance):
        self.timesheets_modal_open = True
        self.timesheets_modal.open()

    def add_hours_label(self):
        hours_label = MDLabel(adaptive_height=True, text=' ', size_hint=(None, None), width=dp(100), halign="center", font_style="H6")
        self.heading_info_box.add_widget(hours_label)

    def add_column_headers(self):
        if self.mode == 'vertical':
            container = self.heading_box
        else:
            container = self.weekday_task_layout
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        column_total = 20
        for column in task_column_data:
            column_total += column[1]
        position = 0
        x = float("{:.4f}".format(10 / column_total))
        position += 10
        task_column_box = MDBoxLayout(orientation='vertical', size_hint=(.95, None), height=self.header_height, padding=0, spacing=0, pos_hint=self.top_center)
        task_column_layout = MDRelativeLayout(size=task_column_box.size, pos_hint=self.top_center)
        for column in task_column_data:
            width = column[1]
            x = float("{:.4f}".format(position / column_total))
            position += width
            task_label = MDLabel(adaptive_height=True, size_hint=(width / column_total, None), text=column[0], font_style="Body1", pos_hint={'x': x, 'center_y': 0.5})
            task_column_layout.add_widget(task_label)
        task_column_box.add_widget(task_column_layout)
        container.add_widget(task_column_box)

    def add_weekdays_box(self):
        self.weekdays_scroller = ScrollView(bar_width = 0, size_hint = (1, 1), pos_hint = self.top_center)
        self.weekdays_view = MDList(adaptive_height=True, spacing=0, pos_hint=self.top_center)
        self.weekdays_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None), pos_hint=self.top_center, spacing=dp(10), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.weekdays_view.add_widget(self.weekdays_box)
        self.weekdays_scroller.add_widget(self.weekdays_view)
        self.timesheet_box.add_widget(self.weekdays_scroller)

    def add_weekday_task_scroller(self):
        if self.mode == 'horizontal':
            self.weekday_task_scroller = ScrollView(bar_width=0, size_hint=(1, 1), pos_hint=self.top_center)
            self.weekday_task_view = MDList(adaptive_height=True, spacing=0, pos_hint=self.top_center)
            self.weekday_task_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(.95, None), pos_hint=self.top_center, md_bg_color=gch('242424'), radius=[dp(20), dp(7), dp(20), dp(7)])
            self.weekday_task_view.add_widget(self.weekday_task_box)
            self.weekday_task_scroller.add_widget(self.weekday_task_view)
            self.weekday_task_layout.add_widget(self.weekday_task_scroller)

    def show_weekdays(self):
        self.weekdays_box.clear_widgets()
        self.weekdays = {}
        self.expanders = {}
        self.totals = {}
        self.loaders = {}
        for weekday in self.app.utils.weekdays:
            self.weekdays[weekday] = self.add_weekday(weekday)
        self.fill_weekdays(self.today[2])

    def add_weekday(self, weekday):
        weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None), pos_hint=self.center_center, md_bg_color=gch('242424'), radius=[dp(20), dp(7), dp(20), dp(7)])
        weekday_heading = MDBoxButton(orientation='horizontal', size_hint=(1, None), height=self.header_height, pos_hint=self.top_center, padding=(dp(15), dp(5), dp(5), dp(5)), on_release=self.expand_weekday)
        weekday_label = MDLabel(adaptive_height=True, text=weekday, font_style="H6", size_hint=(None, None), width=dp(150), pos_hint=self.center_center)
        weekday_heading.add_widget(weekday_label)
        totals_label = MDLabel(adaptive_height=True, text='', size_hint=(None, None), width=dp(50), height=self.header_height, pos_hint=self.center_center, font_style="Body1")
        self.totals[weekday] = totals_label
        weekday_heading.add_widget(totals_label)
        self.add_expanding_box(weekday, weekday_heading)
        weekday_box.add_widget(weekday_heading)
        weekday_tasks = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None), pos_hint=self.top_center)
        if self.today[2] and self.today[2] == weekday and self.mode == 'vertical':
            weekday_tasks.add_widget(MDLabel(adaptive_height=True, text='Loading...', size_hint=(.5, None), height=self.header_height, pos_hint=self.center_center, font_style="Body2"))
        else:
            weekday_tasks.add_widget(MDLabel(text='', size_hint=(1, None), height=5))
        weekday_box.add_widget(weekday_tasks)
        self.weekdays_box.add_widget(weekday_box)
        return weekday_tasks

    def add_expanding_box(self, weekday, weekday_heading):
        expanding_box = MDBoxLayout(size_hint=(None, None), height=dp(20), width=dp(100), padding=[dp(60), 0, 0, 0], spacing=0)
        expand_icon = 'chevron-down' if self.today[2] == weekday else 'chevron-right'
        expanding_box.add_widget(MDIconButton(icon=expand_icon, user_font_size="20sp", pos_hint=self.center_center))
        self.expanders[weekday] = expanding_box
        weekday_heading.add_widget(expanding_box)

    def fill_weekdays(self, weekday: str=None, keep_expanded_state: bool=False):
        for day in self.days:
            tasks = self.tasks[day.dayid]
            dict_tasks = self.app.utils.data_to_dict('task', [task.as_dict() for task in tasks])
            self.fill_weekday_total(day, dict_tasks)
            is_expanding_weekday = self.mode == 'vertical'
            if is_expanding_weekday:
                weekday_box = self.weekdays[day.weekday]
            else:
                weekday_box = self.weekday_task_box
                weekday_box.clear_widgets()
            expand = weekday and day.weekday == weekday
            if expand:
                self.task_edit = TaskEdit(self.task_edit_callback, weekday, self.today[1])
            Clock.schedule_once(partial(self.fill_weekday, day, dict_tasks, weekday_box, expand, is_expanding_weekday, keep_expanded_state))

    def fill_weekday_total(self, day, dict_tasks):
        total = self.totals[day.weekday]
        total.text = f'{self.app.api.get_total(tasks=dict_tasks)}' if dict_tasks else "0:00"

    def fill_weekday(self, day, dict_tasks, weekday_box, expand, is_expanding_weekday, keep_expanded_state, event=None):
        dict_tasks = sorted(dict_tasks, key = lambda i: i['begin'])
        is_expanded = len(weekday_box.children) > (1 if is_expanding_weekday else 0)
        if keep_expanded_state:
            is_expanded = not is_expanded
        if is_expanding_weekday:
            weekday_box.clear_widgets()
        if expand:
            if not is_expanded:
                if dict_tasks:
                    for task in dict_tasks:
                        self.add_task_row(task, weekday_box)
                else:
                    weekday_box.add_widget(MDLabel(text='No tasks entered', size_hint=(1, None), halign='center', height=self.header_height, pos_hint=self.center_center, font_style="Body1"))
                self.weekday = day.weekday
                self.add_new_task_row(weekday_box)
            else:
                weekday_box.add_widget(MDLabel(text='', size_hint=(1, None), height=5))
        elif is_expanding_weekday:
            weekday_box.add_widget(MDLabel(text='', size_hint=(1, None), height=5))

    def add_task_row(self, task, weekday_box):
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        column_total = 20
        for column in task_column_data:
            column_total += column[1]
        position = 0
        x = float("{:.4f}".format(10 / column_total))
        position += 10
        task_row_box = MDBoxButton(orientation='horizontal', size_hint=(1, None), height=self.task_height, on_release=self.task_edit.edit_task)
        task_column_layout = MDRelativeLayout(size=task_row_box.size, pos_hint=self.top_center)
        for column in task_column_data:
            width = column[1]
            x = float("{:.4f}".format(position / column_total))
            position += width
            task_column_value = task[column[2]] if task[column[2]] else '(active)'
            task_label = MDLabel(adaptive_height=True, text=task_column_value, size_hint=(width / column_total, None), font_style="Body1", pos_hint={'x': x, 'center_y': 0.5})
            task_column_layout.add_widget(task_label)
        task_row_box.add_widget(task_column_layout)
        weekday_box.add_widget(task_row_box)

    def task_edit_callback(self, action, original, begin: str=None, end: str=None, code: str=None):
        if action == 'save':
            self.app.api.update_task(original, begin, end, code, self.weekday, begin_date=self.today[1])
        elif action == 'split':
            new_begin = None if begin and original[0] == begin else begin
            new_end = None if end and original[1] == end else end
            self.app.api.split_task(original, code, new_begin, new_end, weekday=self.weekday, begin_date=self.today[1])
        elif action == 'delete':
            original += [self.weekday, self.today[1]]
            self.app.api.remove_task(*original)
        self.refresh_totals_and_tasks(self.weekday)

    def add_new_task_row(self, weekday_box):
        task_row_box = MDBoxButton(orientation='horizontal', size_hint=(1, None), height=self.task_height, md_bg_color=gch('1a1a1a'), radius=[0, dp(0), dp(20), dp(7)], on_release=self.add_new_task)
        task_row_layout = MDRelativeLayout(size=task_row_box.size, pos_hint=self.top_center)
        add_task_button = MDIconButton(icon='plus', user_font_size="20sp", size_hint=(None, None), height=dp(20), width=dp(20), pos_hint=self.center_center)
        task_row_layout.add_widget(add_task_button)
        task_row_box.add_widget(task_row_layout)
        weekday_box.add_widget(task_row_box)

    def add_new_task(self, instance):
        code = os.environ["DEFAULT_PROJECT_CODE"]
        self.app.api.switch_or_start_task(
            code=code,
            weekday=self.weekday,
            begin_date=self.today[1],
            add_new_override=True
        )
        self.refresh_totals_and_tasks(self.weekday)

    def expand_weekday(self, instance, keep_expanded_state: bool=False):
        weekday = instance if isinstance(instance, str) else instance.children[2].text
        self.fill_weekdays(weekday, keep_expanded_state)
        Clock.schedule_once(partial(self.update_expanders, weekday))

    def update_expanders(self, weekday, event):
        is_expanding_weekday = self.mode == 'vertical'
        for day in self.days:
            if is_expanding_weekday:
                weekday_box = self.weekdays[day.weekday]
            else:
                weekday_box = self.weekday_task_box
            expander = self.expanders[day.weekday]
            is_expanded = len(weekday_box.children) > 1
            is_down_chevron = is_expanding_weekday or not is_expanding_weekday and day.weekday == weekday
            expand_icon = 'chevron-down' if is_expanded and is_down_chevron else 'chevron-right'
            expander.clear_widgets()
            expander.add_widget(MDIconButton(icon=expand_icon, user_font_size="20sp", pos_hint=self.center_center))
