from functools import partial
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
from kivymd.uix.floatlayout import  FloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRoundFlatButton, MDTextButton
from kivymd.uix.textfield import MDTextField
from .timepicker import MDTimePicker
from kivy.uix.modalview import ModalView
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.list import TwoLineListItem
from kivymd.toast import toast


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


class TimebotTasksScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotTasksScreen, self).__init__(**kw)
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.today_width = dp(360)
        self.task_width = dp(340)
        self.clear_widgets()
        self.reorienter = Reorienter()
        self.add_widget(self.reorienter)
        self.reorienter.reorient()
        self.add_project_grid()
        self.add_today()
        self.reorienter.callback = self.reorient
        self.reorienter.reorient()
        self.project_modal_open = False
        self.project_modal = self.add_project_modal()
        # self.rotate()

    def on_enter(self):
        if hasattr(self, 'reorienter'):
            self.show_project_grid()
            self.fill_task_grid()

    def reorient(self, reorienter):
        if reorienter.orientation == 'vertical':
            self.project_scroller.size_hint_y = None
            self.project_scroller.height = dp(230)
        else:
            self.project_scroller.size_hint_y = 1
        self.scroll_to_last()

    def rotate(self):
        rotation = Window.rotation
        def rotate(rotation, *args):
            print(rotation)
            Window.rotation = rotation
        Clock.schedule_once(partial(rotate, 90), .5)
        Clock.schedule_once(partial(rotate, rotation), 1)

    def add_project_grid(self):
        self.project_scroller = ScrollView(bar_width = 0, size_hint = (0.9, 1), pos_hint = self.top_center)
        self.project_view = MDList(adaptive_height=True, spacing=dp(10), pos_hint=self.top_center)
        project_label = MDLabel(size_hint=(1, None), height=dp(20), halign="center", text="Select a project to record a task", font_style="Body2", pos_hint={"center_x": .5})
        self.project_view.add_widget(project_label)
        self.project_grid = MDGridLayout(cols=2, padding=dp(10), spacing=dp(20), adaptive_size=True, size_hint=(1, None), pos_hint=self.top_center)
        self.project_view.add_widget(self.project_grid)
        self.project_scroller.add_widget(self.project_view)
        self.reorienter.add_widget(self.project_scroller)
        self.show_project_grid()

    def show_project_grid(self):
        self.project_grid.clear_widgets()
        projects: List[Project] = sorted(self.app.project.get({'show': 1}), key=(lambda p: p.code))
        for project in projects:
            project_card = MD3Card(padding=0, radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(1, None), size=(dp(120), dp(80)), line_color=(1,1,1,1), on_release=self.released)
            project_layout = MDRelativeLayout(size=project_card.size, pos_hint=self.center_center)
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Body1", halign="center", size_hint=(1, None), pos_hint=self.center_center)
            project_desc_float = FloatLayout(top=dp(15))
            project_desc_label = MDLabel(text=project.desc, adaptive_width=True, font_style="Overline", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
            project_desc_float.add_widget(project_desc_label)
            project_layout.add_widget(project_label)
            project_layout.add_widget(project_desc_float)
            project_card.add_widget(project_layout)
            self.project_grid.add_widget(project_card)

    def add_today(self):
        self.get_today()
        self.weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, 1), width=self.today_width, spacing=dp(5), pos_hint=self.top_center)
        self.reorienter.add_widget(self.weekday_box)
        self.fill_weekday_box()

    def get_today(self):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        self.weekday = weekday
        self.day = self.app.day.get({'begin_date': begin_date, 'weekday': weekday})[0]

    def fill_weekday_box(self):
        self.weekday_box.clear_widgets()
        self.add_heading()
        self.add_column_headers()
        self.add_task_grid()
        self.add_last_task_button()
        self.fill_task_grid()
        if hasattr(self, 'show_event'):
            Clock.unschedule(self.show_event)
        self.show_event = Clock.schedule_interval(self.check_active, 1)

    def check_active(self, *args):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        is_same_day = self.weekday == weekday
        if hasattr(self, 'task_view') and self.task_view.children:
            task = self.task_view.children[0]
            labels = list(reversed([c for c in task.children if isinstance(c, MDLabel)]))
            if labels and labels[1].text == '(active)' and self.tasks:
                if not is_same_day:
                    last_task = self.app.api.get_last_task(dayid=day.dayid)
                    self.app.api.update_task(last_task, {'end': '0000'})
                    self.app.api.switch_or_start_task(last_task.code)
                else:
                    last = self.app.utils.data_to_dict('task', [task.as_dict() for task in self.tasks])[-1]
                    labels[2].text = last['total']
        if not is_same_day:
            self.get_today()
            self.fill_weekday_box()

    def add_heading(self):
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint_x=None, width=self.task_width, padding=0, spacing=0, pos_hint=self.top_center)
        weekday_label = MDLabel(adaptive_height=True, text=self.day.weekday[0:3], size_hint_x=None, width=dp(50), font_style="H6")
        timecard: Timecard = self.app.api.get_current_timecard()
        self.heading_box.add_widget(weekday_label)
        self.time_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint_x=None, width=dp(90), padding=0, spacing=0, pos_hint=self.top_center)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_time_label = MDLabel(adaptive_height=True, text=current_time, size_hint_x=None, width=dp(90), font_style="H6")
        self.time_label = current_time_label
        self.time_box.add_widget(current_time_label)
        self.heading_box.add_widget(self.time_box)
        timecard_label = MDLabel(adaptive_height=True, size_hint=(1, None), text=f"Week: {timecard.begin_date} - {timecard.end_date}", font_style="Body2")
        self.heading_box.add_widget(timecard_label)
        if hasattr(self, 'show_time_interval'):
            Clock.unschedule(self.show_time_interval)
        self.show_time_interval = Clock.schedule_interval(self.show_time, 0.1)
        self.weekday_box.add_widget(self.heading_box)

    def add_column_headers(self):
        self.task_column_box = MDBoxLayout(orientation='horizontal', size_hint=(0, None), height=dp(30), width=self.task_width, padding=0, spacing=0, pos_hint=self.top_center)
        task_edit = MDIconButton(icon="pencil", size_hint_x=None, width=dp(15), user_font_size="14sp", pos_hint=self.center_center)
        self.task_column_box.add_widget(task_edit)
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        for task_column in task_column_data:
            task_label = MDLabel(text=task_column[0], size_hint=(None, None), width=dp(task_column[1]), pos_hint=self.center_center, font_style="Body1")
            self.task_column_box.add_widget(task_label)
        task_delete = MDIconButton(icon="close", size_hint_x=None, width=dp(15), user_font_size="14sp", pos_hint=self.center_center)
        self.task_column_box.add_widget(task_delete)
        self.weekday_box.add_widget(self.task_column_box)

    def show_time(self, *args):
        self.time_label.text = datetime.datetime.now().strftime("%H:%M:%S")

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
        task_row_box = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height=dp(50), width=self.task_width, spacing=0, padding=0, md_bg_color=gch('242424'), radius=[dp(20), dp(7), dp(20), dp(7)])
        task_edit = MDIconButton(icon="pencil", size_hint_x=None, width=dp(15),user_font_size="14sp", on_release=self.edit_task, pos_hint=self.center_center)
        task_row_box.add_widget(task_edit)
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        for task_column in task_column_data:
            task_column_value = task[task_column[2]] if task[task_column[2]] else '(active)'
            task_label = MDLabel(text=task_column_value, size_hint=(None, None), width=dp(task_column[1]), pos_hint=self.center_center, font_style="Body2")
            task_row_box.add_widget(task_label)
        task_delete = MDIconButton(icon="close", size_hint_x=None, width=dp(15), user_font_size="14sp", on_release=self.confirm_delete_task, pos_hint=self.center_center)
        task_row_box.add_widget(task_delete)
        self.task_view.add_widget(task_row_box)

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

    def scroll_to_last(self):
        is_scrollable = hasattr(self, 'task_scroller') and hasattr(self, 'task_view')
        has_tasks = hasattr(self, 'weekday_box') and hasattr(self, 'tasks') and self.tasks
        if is_scrollable and has_tasks and self.task_view.children:
            available = self.weekday_box.height - self.heading_box.height - self.task_column_box.height - self.last_task_box.height
            print(self.task_scroller.scroll_y, self.weekday_box.height, self.heading_box.height, self.task_column_box.height, self.last_task_box.height, self.task_view.height, available)
            if self.task_view.height > available and self.task_scroller.height != 100:
                self.task_scroller.scroll_to(self.task_view.children[0])

    def edit_task(self, instance):
        labels = [c.text for c in instance.parent.children]
        self.original_values = [labels[4], labels[3], labels[1]]
        edit_dialog = TimebotEditTaskDialog()
        self.custom_dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=edit_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)],
            buttons=[
                MDFlatButton(
                    text="SAVE", text_color=self.app.theme_cls.primary_color,
                    on_release=self.save_task
                ),
            ],
        )
        self.custom_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.custom_dialog.open()
        self.custom_dialog.content_cls.ids.begin_time.on_release = self.open_begin_time
        self.custom_dialog.content_cls.ids.end_time.on_release = self.open_end_time
        self.custom_dialog.content_cls.ids.project_label.text = self.original_values[2]
        self.custom_dialog.content_cls.ids.project_card.on_release = self.choose_project
        self.custom_dialog.content_cls.ids.begin.text = self.original_values[0]
        self.custom_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.original_values[1] 

    def add_project_modal(self):
        modal = ModalView(size_hint=(None, None), height=dp(340), width=dp(280), auto_dismiss=True)
        modal_box = MDBoxLayout(orientation="vertical", size_hint=(1,1), pos_hint=self.top_center, padding=[dp(5),dp(5),dp(5),dp(5)])
        modal_text = MDLabel(text="Select a project code:", size_hint=(None, None), height=dp(50), width=dp(200), pos_hint=self.top_center, font_style="H6")
        modal_box.add_widget(modal_text)
        view = ScrollView()
        self.project_list = MDSelectionList(spacing=dp(12))
        view.add_widget(self.project_list)
        modal_box.add_widget(view)
        modal.add_widget(modal_box)
        return modal

    def choose_project(self, *args):
        self.project_list.clear_widgets()
        projects: List[Project] = sorted(self.app.project.get(), key=(lambda p: p.code))
        for project in projects:
            self.project_list.add_widget(TwoLineListItem(
                text=project.code,
                secondary_text=project.desc,
                _no_ripple_effect=True,
                on_release=self.selected,
                secondary_font_style="Body2"
            ))
        self.project_modal_open = True
        self.project_modal.open()

    def selected(self, instance):
        self.custom_dialog.content_cls.ids.project_label.text = instance.text
        self.project_modal.dismiss()

    def open_begin_time(self, *args):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_begin_time)
        begin_time = self.custom_dialog.content_cls.ids.begin.text
        begin_time_str = f"{begin_time[0:2]}:{begin_time[2:4]}:00"
        begin_time_time = datetime.datetime.strptime(begin_time_str, '%H:%M:%S').time()
        time_dialog.set_time(begin_time_time)
        time_dialog.open()

    def open_end_time(self, *args):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_end_time)
        end_time = self.custom_dialog.content_cls.ids.end.text
        end_time_str = f"{end_time[0:2]}:{end_time[2:4]}:00"
        end_time_time = datetime.datetime.strptime(end_time_str, '%H:%M:%S').time()
        time_dialog.set_time(end_time_time)
        time_dialog.open()

    def get_begin_time(self, *args):
        print(args)
        self.custom_dialog.content_cls.ids.begin.text = self.app.utils.db_format_time(args[0])

    def get_end_time(self, *args):
        print(args)
        self.custom_dialog.content_cls.ids.end.text = self.app.utils.db_format_time(args[0])

    def released(self, instance):
        self.app.api.switch_or_start_task(instance.children[0].children[1].text)
        self.fill_task_grid()
        self.scroll_to_last()

    def cancel_dialog(self, *args):
        self.custom_dialog.dismiss(force=True)

    def save_task(self, *args):
        begin = self.custom_dialog.content_cls.ids.begin.text
        end = self.custom_dialog.content_cls.ids.end.text
        code = self.custom_dialog.content_cls.ids.project_label.text
        error = self.app.api.update_task(self.original_values, begin, end, code)
        if error:
            self.custom_dialog.content_cls.ids.error.text = error
        else:
            self.custom_dialog.dismiss(force=True)
            self.fill_task_grid()

    def confirm_delete_task(self, instance):
        labels = [c.text for c in instance.parent.children]
        self.remove_me = [labels[4], labels[3], labels[1]]
        confirm_dialog = TimebotConfirmDeleteTaskDialog()
        self.custom_dialog = MDDialog(
            title="Delete Task",
            type="custom",
            content_cls=confirm_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)],
            buttons=[
                MDFlatButton(
                    text="DELETE", text_color=self.app.theme_cls.primary_color,
                    on_release=self.delete_task
                ),
            ],
        )
        self.custom_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {self.remove_me[0]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {self.remove_me[1]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {self.remove_me[2]}'
        self.custom_dialog.open()

    def delete_task(self, instance):
        self.custom_dialog.dismiss(force=True)
        self.app.api.remove_task(*self.remove_me)
        self.fill_task_grid()

    def end_task(self, instance):
        self.app.api.switch_or_start_task()
        self.fill_task_grid()

    def continue_task(self, instance):
        self.app.api.resume_task()
        self.fill_task_grid()


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass