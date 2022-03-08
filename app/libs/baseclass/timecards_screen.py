import datetime
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
    def on_enter(self):
        self.clear_widgets()
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

    def add_heading(self):
        heading_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(.9, None))
        timecard_label = MDLabel(adaptive_height=True, text=f"Week of: {self.timecard.begin_date} - {self.timecard.end_date}", font_style="Body2")
        heading_box.add_widget(timecard_label)
        entry_column_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for column in entry_column_data:
            entry_label = MDLabel(adaptive_height=True, text=column[0], size_hint=(None, None), width=dp(column[1]), font_style="Body1")
            entry_column_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", pos_hint={"center_x": .5, "center_y": .5})
        entry_column_box.add_widget(entry_delete)
        heading_box.add_widget(entry_column_box)
        self.view.add_widget(heading_box)

    def show_weekdays(self):
        self.weekdays_box.clear_widgets()
        spinner = MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)), pos_hint={'center_x': .5, 'center_y': .5}, active=True)
        self.weekdays_box.add_widget(spinner)
        Clock.schedule_once(self.show_weekdays_once)

    def show_weekdays_once(self, event=None):
        days = Service(Day).get({'begin_date': self.timecard.begin_date})
        days_rows = days if isinstance(days, list) else [days]
        widgets = []
        for day in days_rows:
            widgets += self.get_weekday(day)
        self.weekdays_box.clear_widgets()
        for widget in widgets:
            self.weekdays_box.add_widget(widget)

    def get_weekday(self, day):
        widgets = []
        weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(0.9, None))
        weekday_label = MDLabel(adaptive_height=True, text=day.weekday, font_style="H6")
        widgets.append(weekday_label)
        entries = Service(Entry).get({'dayid': day.dayid})
        if entries:
            dict_entries = Utils.data_to_dict('entry', [entry.as_dict() for entry in entries])
            for entry in dict_entries:
                widgets += self.get_entry(entry, weekday_box)
        return widgets

    def get_entry(self, entry, weekday_box):
        entry_row_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height="30dp", pos_hint={"center_x": .5, "center_y": .5})
        entry_edit = MDIconButton(icon="pencil", user_font_size="14sp", on_release=self.edit_task, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_edit)
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for column in entry_column_data:
            entry_column_value = entry[column[2]] if entry[column[2]] else '(active)'
            entry_label = MDLabel(adaptive_height=True, text=entry_column_value, size_hint=(None, None), width=dp(column[1]), pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2")
            entry_row_box.add_widget(entry_label)
        entry_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.confirm_delete_entry, pos_hint={"center_x": .5, "center_y": .5})
        entry_row_box.add_widget(entry_delete)
        return [entry_row_box]

    def edit_task(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children]
        app = App.get_running_app()
        edit_dialog = TimebotTimecardEditTaskDialog()
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
        self.original_values = [labels[4], labels[3], labels[1], parent_labels[0]]
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
            self.show_weekdays()

    def confirm_delete_entry(self, instance):
        parent_labels = [c.text for c in instance.parent.parent.children if isinstance(c, MDLabel)]
        labels = [c.text for c in instance.parent.children]
        self.remove_me = [labels[4], labels[3], labels[1], parent_labels[0]]
        app = App.get_running_app()
        confirm_dialog = TimebotTimecardConfirmDeleteTaskDialog()
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
        self.custom_dialog.content_cls.ids.weekday.text = f'Weekday: {self.remove_me[3]}'
        self.custom_dialog.content_cls.ids.begin.text = f'Begin: {self.remove_me[0]}'
        self.custom_dialog.content_cls.ids.end.text = f'End: {"" if self.remove_me[1] == "(active)" else self.remove_me[1]}'
        self.custom_dialog.content_cls.ids.code.text = f'Code: {self.remove_me[2]}'
        self.custom_dialog.open()

    def delete_entry(self, instance):
        self.custom_dialog.dismiss(force=True)
        API.remove_task(*self.remove_me)
        self.show_weekdays()
