import os, datetime
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
from kivymd.uix.list import TwoLineListItem
from kivymd.toast import toast
from project import Project


class TimebotEditTaskDialog(MDBoxLayout):
    pass


class TimebotConfirmDeleteTaskDialog(MDBoxLayout):
    pass


class TaskEdit():

    def __init__(self, callback, weekday: str=None, begin_date: str=None):
        self.callback = callback
        self.weekday = weekday
        self.begin_date = begin_date
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.project_modal_open = False
        self.project_modal = self.add_project_modal()

    def edit_task(self, instance):
        labels = [c.text for c in instance.children[0].children]
        self.original_values = [labels[3], labels[2], labels[0]]
        edit_dialog = TimebotEditTaskDialog()
        self.edit_dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=edit_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)],
            buttons=[
                MDFlatButton(
                    text="SPLIT",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.split_task
                ),
                MDFlatButton(
                    text="DELETE",
                    text_color=gch('903030'),
                    on_release=self.confirm_delete_task
                ),
                MDFlatButton(
                    text="SAVE",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.save_task
                ),
            ],
        )
        self.edit_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.edit_dialog.open()
        self.time_touch = ''
        self.edit_begin_value = self.app.utils.am_pm_format(self.original_values[0])
        self.edit_end_value = self.app.utils.am_pm_format(self.app.utils.db_format_time(datetime.datetime.now().time()) if self.original_values[1] == '(active)' else self.original_values[1])
        self.edit_dialog.content_cls.ids.begin_time.on_press = self.on_press_begin
        self.edit_dialog.content_cls.ids.begin_time.on_touch_move = self.on_touch_move_begin
        self.edit_dialog.content_cls.ids.begin_time.on_touch_up = self.on_touch_up_begin
        self.edit_dialog.content_cls.ids.end_time.on_press = self.on_press_end
        self.edit_dialog.content_cls.ids.end_time.on_touch_move = self.on_touch_move_end
        self.edit_dialog.content_cls.ids.end_time.on_touch_up = self.on_touch_up_end
        self.edit_dialog.content_cls.ids.project_label.text = self.original_values[2]
        self.edit_dialog.content_cls.ids.project_card.on_release = self.choose_project
        self.edit_dialog.content_cls.ids.begin.text = self.app.utils.am_pm_format(self.original_values[0])
        self.edit_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.app.utils.am_pm_format(self.original_values[1])
        # Clock.schedule_once(self.edit_tap_target, 1)

    def edit_tap_target(self, *args):
        tap_target_view = MDTapTargetView(
            widget=self.edit_dialog.content_cls.ids.begin_time,
            title_text='Time slider',
            description_text='tap and slide to adjust time',
            widget_position='right',
            title_position='left',
            target_circle_color=(0, 0, 0),
            stop_on_target_touch=True,
            stop_on_outer_touch=True
        )
        tap_target_view.start()

    def on_press_begin(self, *args):
        self.time_touch = 'begin'
        self.set_time_min_max(self.edit_begin_value)

    def set_time_min_max(self, time_str: str):
        time_min = datetime.datetime.strptime('01/01/0001 00:00', '%m/%d/%Y %H:%M')
        time_max = datetime.datetime.strptime('01/01/0001 23:59', '%m/%d/%Y %H:%M')
        obj_time = datetime.datetime.strptime(f'01/01/0001 {time_str}', '%m/%d/%Y %I:%M %p') if time_str else None
        self.change_min = int((time_min - obj_time).total_seconds() / 60) if time_str else None
        self.change_max= int((time_max - obj_time).total_seconds() / 60) if time_str else None

    def on_touch_move_begin(self, touch):
        if self.time_touch == 'begin':
            time_change = int((touch.oy - touch.pos[1]) / 20)
            if self.change_min is not None and time_change < self.change_min:
                time_change = self.change_min
            if self.change_min is not None and time_change > self.change_max:
                time_change = self.change_max
            if time_change == 0:
                return
            updated_time_str = self.app.utils.db_format_add_time(self.edit_begin_value, time_change)
            end = self.edit_dialog.content_cls.ids.end.text
            end = self.app.utils.db_format_time(self.app.utils.obj_format_time(end))
            if end and updated_time_str >= end:
                updated_time_str = self.app.utils.db_format_add_time(end, -1)
            updated_time_str = self.app.utils.am_pm_format(updated_time_str)
            self.edit_dialog.content_cls.ids.begin.text = updated_time_str

    def on_touch_up_begin(self, *args):
        if self.time_touch == 'begin':
            self.edit_begin_value = self.edit_dialog.content_cls.ids.begin.text

    def on_press_end(self, *args):
        self.time_touch = 'end'
        self.set_time_min_max(self.edit_end_value)

    def on_touch_move_end(self, touch):
        if self.time_touch == 'end':
            time_change = int((touch.oy - touch.pos[1])/ 20)
            if self.change_min is not None and time_change < self.change_min:
                time_change = self.change_min
            if self.change_min is not None and time_change > self.change_max:
                time_change = self.change_max
            if time_change == 0:
                return
            updated_time_str = self.app.utils.db_format_add_time(self.edit_end_value, time_change)
            begin = self.edit_dialog.content_cls.ids.begin.text
            begin = self.app.utils.db_format_time(self.app.utils.obj_format_time(begin))
            if updated_time_str <= begin:
                updated_time_str = self.app.utils.db_format_add_time(begin, 1)
            updated_time_str = self.app.utils.am_pm_format(updated_time_str)
            self.edit_dialog.content_cls.ids.end.text = updated_time_str

    def on_touch_up_end(self, *args):
        if self.time_touch == 'end':
            self.edit_end_value = self.edit_dialog.content_cls.ids.end.text

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
        self.edit_dialog.content_cls.ids.project_label.text = instance.text
        self.project_modal.dismiss()

    def cancel_dialog(self, *args):
        self.edit_dialog.dismiss(force=True)

    def split_task(self, *args):
        ids = self.edit_dialog.content_cls.ids
        begin = ids.begin.text
        begin = self.app.utils.db_format_time(self.app.utils.obj_format_time(begin))
        end = ids.end.text
        end = self.app.utils.db_format_time(self.app.utils.obj_format_time(end)) if end else ''
        code = ids.project_label.text if ids.project_label.text != self.original_values[2] else os.environ.get('DEFAULT_PROJECT_CODE')
        new_begin = None if begin and self.original_values[0] == begin else begin
        new_end = None if end and self.original_values[1] == end else end
        error = self.app.api.split_task_error_check(self.original_values, code, new_begin, new_end, weekday=self.weekday, begin_date=self.begin_date)
        if isinstance(error, str):
            self.edit_dialog.content_cls.ids.error.text = error
        else:
            self.edit_dialog.dismiss(force=True)
            self.callback('split', self.original_values, begin, end, code)
            toast('Split task')

    def save_task(self, *args):
        ids = self.edit_dialog.content_cls.ids
        begin = ids.begin.text
        begin = self.app.utils.db_format_time(self.app.utils.obj_format_time(begin))
        end = ids.end.text
        end = self.app.utils.db_format_time(self.app.utils.obj_format_time(end)) if end else ''
        code = ids.project_label.text
        error = self.app.api.update_task_error_check(self.original_values, begin, end, code, weekday=self.weekday, begin_date=self.begin_date)
        if isinstance(error, str):
            self.edit_dialog.content_cls.ids.error.text = error
        else:
            self.edit_dialog.dismiss(force=True)
            self.callback('save', self.original_values, begin, end, code)
            toast('Saved task')

    def confirm_delete_task(self, instance):
        confirm_dialog = TimebotConfirmDeleteTaskDialog()
        self.confirm_dialog = MDDialog(
            title="Delete Task",
            type="custom",
            content_cls=confirm_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)],
            buttons=[
                MDFlatButton(
                    text="CONFIRM",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.delete_task
                ),
            ],
        )
        self.confirm_dialog.md_bg_color = self.app.theme_cls.bg_dark
        self.confirm_dialog.content_cls.ids.begin.text = f'Begin: {self.original_values[0]}'
        self.confirm_dialog.content_cls.ids.end.text = f'End: {self.original_values[1]}'
        self.confirm_dialog.content_cls.ids.code.text = f'Code: {self.original_values[2]}'
        self.confirm_dialog.open()

    def delete_task(self, instance):
        self.confirm_dialog.dismiss(force=True)
        self.edit_dialog.dismiss(force=True)
        self.callback('delete', self.original_values)
        toast('Deleted task')
