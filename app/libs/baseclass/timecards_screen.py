
import os
from functools import partial
from kivy.utils import get_color_from_hex as gch
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.modalview import ModalView
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.list import OneLineListItem
from kivymd.toast import toast


class TimebotTimecardEditTaskDialog(MDBoxLayout):
    pass


class TimebotTimecardConfirmDeleteTaskDialog(MDBoxLayout):
    pass


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass


class TimebotTimecardsScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotTimecardsScreen, self).__init__(**kw)
        self.app = App.get_running_app()
        self.custom_dialog = None
        self.timesheets_modal_open = False
        self.timesheets_modal = self.add_timesheets_modal()
        self.top_center = {"center_x": .5, "top": 1}
        self.mid_center = {"center_x": .5, "top": .80}
        self.center_center = {"center_x": .5, "center_y": .5}
        self.today_width = dp(360)
        self.task_width = dp(360)
        self.weekday_width = dp(340)
        self.heading_height = dp(35)
        self.header_height = dp(30)
        self.task_height = dp(50)
        Clock.schedule_once(self.load_current_timesheet, 2)

    def add_timesheets_modal(self):
        modal = ModalView(size_hint=(.8, .8), auto_dismiss=False)
        view = ScrollView()
        timecard_list = MDSelectionList(spacing=dp(12))
        for timecard in self.app.timecard.get():
            timecard_list.add_widget(OneLineListItem(
                text=f"Week of: {timecard.begin_date} - {timecard.end_date}",
                _no_ripple_effect=True,
                on_release=self.selected
            ))
        view.add_widget(timecard_list)
        modal.add_widget(view)
        return modal

    def selected(self, instance):
        toast(f'loading {instance.text}')
        begin_date = instance.text.split(': ')[1].split(' - ')[0]
        self.timecard = self.app.timecard.get(begin_date)
        self.timesheets_modal.dismiss()
        self.load_timesheet_data()

    def load_current_timesheet(self, *args):
        self.clear_widgets()
        self.today = self.app.utils.get_begin_date()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = self.top_center
        self.view = MDList(spacing=dp(10))
        self.timecard: Timecard = self.app.api.get_current_timecard()
        self.scroller.add_widget(self.view)
        self.add_widget(self.scroller)
        self.load_timesheet_data()

    def load_timesheet_data(self):
        self.view.clear_widgets()
        self.add_heading()
        self.weekdays_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None), pos_hint=self.top_center)
        self.show_weekdays()
        self.view.add_widget(self.weekdays_box)

    def on_enter(self):
        self.today = self.app.utils.get_begin_date()
        self.fill_weekdays(self.today[2])
        self.set_hours()

    def set_hours(self):
        self.heading_info_box.children[0].text = f'Total: {self.app.api.get_total()}'

    def add_heading(self):
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint_x=None, width=self.task_width, padding=0, spacing=0, pos_hint=self.top_center)
        self.heading_info_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(None, None), width=self.task_width, height=self.heading_height, padding=0, spacing=0, pos_hint=self.top_center)
        timecard_card = MDCard(padding=0, radius=[dp(7), dp(7), dp(7), dp(7)], size_hint=(None, None), width=dp(230), height=dp(30), on_release=self.choose_timesheet, line_color=(1,1,1,1))
        timecard_layout = MDRelativeLayout(size=timecard_card.size, pos_hint=self.center_center)
        timecard_label = MDLabel(adaptive_height=True, text=f"Week of: {self.timecard.begin_date} - {self.timecard.end_date}", size_hint=(None, None), width=dp(200), height=dp(30), pos_hint={"center_x": .45, "center_y": .5}, font_style="Body2")
        timecard_layout.add_widget(timecard_label)
        select_icon = MDIconButton(icon='chevron-down', user_font_size="20sp", pos_hint={"center_x": .95, "center_y": .5})
        timecard_layout.add_widget(select_icon)
        timecard_card.add_widget(timecard_layout)
        self.heading_info_box.add_widget(timecard_card)
        hours_label = MDLabel(adaptive_height=True, text=f'Total: {self.app.api.get_total()}', size_hint=(None, None), width=dp(100), halign="center", font_style="Body1")
        self.heading_info_box.add_widget(hours_label)
        self.heading_box.add_widget(self.heading_info_box)
        self.add_column_headers(self.heading_box)
        self.view.add_widget(self.heading_box)

    def choose_timesheet(self, instance):
        self.timesheets_modal_open = True
        self.timesheets_modal.open()

    def add_column_headers(self, heading_box):
        task_column_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=self.header_height, pos_hint=self.top_center)
        task_edit = MDIconButton(icon="pencil", user_font_size="14sp", pos_hint=self.center_center)
        task_column_box.add_widget(task_edit)
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        for column in task_column_data:
            task_label = MDLabel(adaptive_height=True, text=column[0], size_hint=(None, None), width=dp(column[1]), font_style="Body1")
            task_column_box.add_widget(task_label)
        task_delete = MDIconButton(icon="close", user_font_size="14sp", pos_hint=self.center_center)
        task_column_box.add_widget(task_delete)
        heading_box.add_widget(task_column_box)

    def show_weekdays(self):
        self.weekdays_box.clear_widgets()
        self.weekdays = {}
        self.expanders = {}
        self.totals = {}
        self.loaders = {}
        for weekday in self.app.utils.weekdays:
            self.weekdays[weekday] = self.add_weekday(weekday)
        self.fill_weekdays(weekday)

    def add_weekday(self, weekday):
        weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, None), width=self.weekday_width, pos_hint=self.center_center, md_bg_color=gch('242424'), radius=[dp(20), dp(7), dp(20), dp(7)])
        weekday_heading = MDBoxLayout(orientation='horizontal', size_hint=(None, None), width=self.weekday_width, height=self.header_height, pos_hint=self.top_center, padding=(dp(5), dp(5), dp(5), dp(5)))
        weekday_label = MDLabel(adaptive_height=True, text=weekday, font_style="H6", size_hint=(None, None), width=dp(120), pos_hint=self.mid_center)
        weekday_heading.add_widget(weekday_label)
        add_task = MDIconButton(icon='plus', on_release=self.add_new_task, user_font_size="20sp", pos_hint=self.center_center)
        weekday_heading.add_widget(add_task)
        totals_label = MDLabel(adaptive_height=True, text='', size_hint=(None, None), width=dp(80), height=self.header_height, pos_hint=self.center_center, font_style="Body2")
        self.totals[weekday] = totals_label
        weekday_heading.add_widget(totals_label)
        expanding_box = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height=dp(20), width=dp(20))
        if self.today[2] != weekday:
            expanding_box.add_widget(MDIconButton(icon='arrow-expand-vertical', on_release=self.expand_weekday, user_font_size="20sp", pos_hint=self.center_center))
        self.expanders[weekday] = expanding_box
        weekday_heading.add_widget(expanding_box)
        weekday_box.add_widget(weekday_heading)
        weekday_tasks = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None), pos_hint=self.top_center)
        if self.today[2] == weekday:
            weekday_tasks.add_widget(MDLabel(adaptive_height=True, text='Loading...', size_hint=(.5, None), height=self.header_height, pos_hint=self.center_center, font_style="Body2"))
        else:
            weekday_tasks.add_widget(MDLabel(text='', size_hint=(1, None), height=10))
        weekday_box.add_widget(weekday_tasks)
        self.view.add_widget(weekday_box)
        return weekday_tasks

    def add_new_task(self, instance):
        code = os.environ["DEFAULT_PROJECT_CODE"]
        weekday: str = instance.parent.children[3].text
        self.app.api.switch_or_start_task(code=code, weekday=weekday)
        self.fill_weekdays(weekday)

    def expand_weekday(self, instance):
        weekday = instance.parent.parent.children[3].text
        self.fill_weekdays(weekday)
        box = self.weekdays[weekday]
        values = (True, None, box.height, 1, False)
        (box.adaptive_height, box.size_hint_y, box.height, box.opacity, box.disabled) = values
        expander = self.expanders[weekday]
        expander.clear_widgets()

    def fill_weekdays(self, weekday:str=None):
        print(f'begin_date: {self.timecard.begin_date}')
        days = self.app.day.get({'begin_date': self.timecard.begin_date})
        days_rows = days if isinstance(days, list) else [days]
        print(f'days count: {len(days_rows)}')
        for day in days_rows:
            total = self.totals[day.weekday]
            total.text = f'Total: {self.app.api.get_total(day.weekday, day.dayid)}'
            if not weekday or (weekday and day.weekday == weekday):
                Clock.schedule_once(partial(self.fill_weekday, day))

    def fill_weekday(self, day, event):
        weekday_box = self.weekdays[day.weekday]
        weekday_box.clear_widgets()
        tasks = self.app.task.get({'dayid': day.dayid})
        if tasks:
            dict_tasks = self.app.utils.data_to_dict('task', [task.as_dict() for task in tasks])
            for task in dict_tasks:
                self.add_task(task, weekday_box)
        else:
            weekday_box.add_widget(MDLabel(text='No tasks entered', size_hint=(1, None), halign='center', height=self.header_height, pos_hint=self.center_center, font_style="Body2"))

    def add_task(self, task, weekday_box):
        task_row_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=self.task_height)
        task_edit = MDIconButton(icon="pencil", user_font_size="14sp", on_release=self.edit_task, pos_hint=self.center_center)
        task_row_box.add_widget(task_edit)
        task_column_data = self.app.utils.schema_dict_to_tuple('task')
        for column in task_column_data:
            task_column_value = task[column[2]] if task[column[2]] else '(active)'
            task_label = MDLabel(adaptive_height=True, text=task_column_value, size_hint=(None, None), width=dp(column[1]), pos_hint=self.center_center, font_style="Body2")
            task_row_box.add_widget(task_label)
        task_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.confirm_delete_task, pos_hint=self.center_center)
        task_row_box.add_widget(task_delete)
        weekday_box.add_widget(task_row_box)

    def edit_task(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.parent.children[1].children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children if c.text]
        edit_dialog = TimebotTimecardEditTaskDialog()
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
        self.original_values = [labels[3], labels[2], labels[0], parent_labels[1]]
        self.custom_dialog.content_cls.ids.weekday.text = f'Weekday: {self.original_values[3]}'
        self.custom_dialog.content_cls.ids.begin.text = self.original_values[0]
        self.custom_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.original_values[1] 
        self.custom_dialog.content_cls.ids.code.text = self.original_values[2]

    def cancel_dialog(self, *args):
        self.custom_dialog.dismiss(force=True)

    def save_task(self, *args):
        weekday = self.original_values[3]
        begin = self.custom_dialog.content_cls.ids.begin.text
        end = self.custom_dialog.content_cls.ids.end.text
        code = self.custom_dialog.content_cls.ids.code.text
        error = self.app.api.update_task(self.original_values, begin, end, code, weekday)
        if error:
            self.custom_dialog.content_cls.ids.error.text = error
        else:
            self.custom_dialog.dismiss(force=True)
            self.fill_weekdays(weekday)

    def confirm_delete_task(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.parent.children[1].children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children if c.text]
        self.remove_me = [labels[3], labels[2], labels[0], parent_labels[1]]
        confirm_dialog = TimebotTimecardConfirmDeleteTaskDialog()
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
        self.custom_dialog.content_cls.ids.weekday.text = f'Weekday: {self.remove_me[3]}'
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {self.remove_me[0]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {"" if self.remove_me[1] == "(active)" else self.remove_me[1]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {self.remove_me[2]}'
        self.custom_dialog.open()

    def delete_task(self, instance):
        self.custom_dialog.dismiss(force=True)
        self.app.api.remove_task(*self.remove_me)
        self.fill_weekdays(self.remove_me[3])
