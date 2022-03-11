from functools import partial
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from pyparsing import col
from api import API
from service import Service
from day import Day
from timecard import Timecard
from entry import Entry
from utils import Utils


class TimebotTimecardEditTaskDialog(MDBoxLayout):
    pass


class TimebotTimecardConfirmDeleteTaskDialog(MDBoxLayout):
    pass


class TimebotTimecardsScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotTimecardsScreen, self).__init__(**kw)
        self.custom_dialog = None
        Clock.schedule_once(self.load_timesheet, 2)

    def load_timesheet(self, *args):
        self.clear_widgets()
        self.today = Utils.get_begin_date()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}
        self.view = MDList(spacing=dp(10))
        self.timecard: Timecard = API.get_current_timecard()
        self.add_heading()
        self.weekdays_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None))
        self.show_weekdays()
        self.view.add_widget(self.weekdays_box)
        self.scroller.add_widget(self.view)
        self.add_widget(self.scroller)

    def on_enter(self):
        self.today = Utils.get_begin_date()
        self.fill_weekdays(self.today[2])
        self.set_hours()

    def set_hours(self):
        self.heading_info_box.children[0].text = f'Total: {API.get_total()}'

    def add_heading(self):
        self.heading_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint_x=None, width="340dp", padding="0dp", spacing="0dp")
        self.heading_info_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(None, None), width="340dp", height="35dp", padding="0dp", spacing="0dp")
        timecard_label = MDLabel(adaptive_height=True, text=f"Week of: {self.timecard.begin_date} - {self.timecard.end_date}", size_hint=(None, None), width="240dp", font_style="Body2")
        self.heading_info_box.add_widget(timecard_label)
        hours_label = MDLabel(adaptive_height=True, text=f'Total: {API.get_total()}', size_hint=(None, None), width="80dp", font_style="Body2")
        self.heading_info_box.add_widget(hours_label)
        self.heading_box.add_widget(self.heading_info_box)
        self.add_column_headers(self.heading_box)
        self.view.add_widget(self.heading_box)

    def add_column_headers(self, heading_box):
        entry_column_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height="30dp", pos_hint={"center_x": .5, "center_y": .5})
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for column in entry_column_data:
            entry_label = MDLabel(adaptive_height=True, text=column[0], size_hint=(None, None), width=dp(column[1]), font_style="Body1")
            entry_column_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_delete)
        heading_box.add_widget(entry_column_box)

    def show_weekdays(self):
        self.weekdays_box.clear_widgets()
        self.weekdays = {}
        self.expanders = {}
        self.totals = {}
        self.loaders = {}
        for weekday in Utils.weekdays:
            self.weekdays[weekday] = self.add_weekday(weekday)
        self.fill_weekdays(weekday)

    def add_weekday(self, weekday):
        weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(None, None), width="300dp")
        weekday_heading = MDBoxLayout(orientation='horizontal', size_hint=(None, None), width="300dp", height="30dp")
        weekday_label = MDLabel(adaptive_height=True, text=weekday, font_style="H6", size_hint=(None, None), width="120dp")
        weekday_heading.add_widget(weekday_label)
        add_task = MDIconButton(icon='plus', on_release=self.add_task, user_font_size="20sp", pos_hint={"center_x": .5, "center_y": .5})
        weekday_heading.add_widget(add_task)
        totals_label = MDLabel(adaptive_height=True, text='', size_hint=(None, None), width="80dp", height="30dp", pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2")
        self.totals[weekday] = totals_label
        weekday_heading.add_widget(totals_label)
        expanding_box = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height='20dp', width='20dp')
        if self.today[2] != weekday:
            expanding_box.add_widget(MDIconButton(icon='arrow-expand-vertical', on_release=self.expand_weekday, user_font_size="20sp", pos_hint={"center_x": .5, "center_y": .5}))
        self.expanders[weekday] = expanding_box
        weekday_heading.add_widget(expanding_box)
        weekday_box.add_widget(weekday_heading)
        weekday_entries = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(1, None))
        if self.today[2] == weekday:
            weekday_entries.add_widget(MDLabel(adaptive_height=True, text='Loading...', size_hint=(.5, None), height="30dp", pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2"))
        else:
            weekday_entries.add_widget(MDLabel(text='', size_hint=(1, None), height=10))
        weekday_box.add_widget(weekday_entries)
        self.view.add_widget(weekday_box)
        return weekday_entries

    def add_task(self, instance):
        code = API.get_setting('default_project_code').value
        weekday: str = instance.parent.children[3].text
        API.switch_or_start_task(code=code, weekday=weekday)
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
        days = Service(Day).get({'begin_date': self.timecard.begin_date})
        days_rows = days if isinstance(days, list) else [days]
        for day in days_rows:
            total = self.totals[day.weekday]
            total.text = f'Total: {API.get_total(day.weekday)}'
            if not weekday or (weekday and day.weekday == weekday):
                Clock.schedule_once(partial(self.fill_weekday, day))

    def fill_weekday(self, day, event):
        weekday_box = self.weekdays[day.weekday]
        weekday_box.clear_widgets()
        entries = Service(Entry).get({'dayid': day.dayid})
        if entries:
            dict_entries = Utils.data_to_dict('entry', [entry.as_dict() for entry in entries])
            for entry in dict_entries:
                self.add_entry(entry, weekday_box)
        else:
            weekday_box.add_widget(MDLabel(text='No tasks entered', size_hint=(1, None), halign='center', height="30dp", pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2"))

    def add_entry(self, entry, weekday_box):
        entry_row_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height="50dp", pos_hint={"center_x": .5, "center_y": .5})
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", on_release=self.edit_task, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for column in entry_column_data:
            entry_column_value = entry[column[2]] if entry[column[2]] else '(active)'
            entry_label = MDLabel(adaptive_height=True, text=entry_column_value, size_hint=(None, None), width=dp(column[1]), pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2")
            entry_row_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.confirm_delete_entry, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_delete)
        weekday_box.add_widget(entry_row_box)

    def edit_task(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.parent.children[1].children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children if c.text]
        app = App.get_running_app()
        edit_dialog = TimebotTimecardEditTaskDialog()
        self.custom_dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=edit_dialog,
            radius=[20, 7, 20, 7],
            buttons=[
                MDFlatButton(
                    text="SAVE", text_color=app.theme_cls.primary_color,
                    on_release=self.save_task
                ),
            ],
        )
        self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
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
        error = API.update_task(self.original_values, begin, end, code, weekday)
        if error:
            self.custom_dialog.content_cls.ids.error.text = error
        else:
            self.custom_dialog.dismiss(force=True)
            self.fill_weekdays(weekday)

    def confirm_delete_entry(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.parent.children[1].children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children if c.text]
        self.remove_me = [labels[3], labels[2], labels[0], parent_labels[1]]
        app = App.get_running_app()
        confirm_dialog = TimebotTimecardConfirmDeleteTaskDialog()
        self.custom_dialog = MDDialog(
            title="Delete Task",
            type="custom",
            content_cls=confirm_dialog,
            radius=[20, 7, 20, 7],
            buttons=[
                MDFlatButton(
                    text="DELETE", text_color=app.theme_cls.primary_color,
                    on_release=self.delete_entry
                ),
            ],
        )
        self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
        self.custom_dialog.content_cls.ids.weekday.text = f'Weekday: {self.remove_me[3]}'
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {self.remove_me[0]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {"" if self.remove_me[1] == "(active)" else self.remove_me[1]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {self.remove_me[2]}'
        self.custom_dialog.open()

    def delete_entry(self, instance):
        self.custom_dialog.dismiss(force=True)
        API.remove_task(*self.remove_me)
        self.fill_weekdays(self.remove_me[3])
