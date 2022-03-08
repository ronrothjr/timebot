import datetime
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.effects.stiffscroll import StiffScrollEffect
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
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


class TimebotTimecardsScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        # self.scroller.effect_cls = StiffScrollEffect
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}

        view = MDList(spacing=dp(10))

        heading_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(0.9, None))
        timecard: Timecard = API.get_current_timecard()
        timecard_label = MDLabel(adaptive_height=True, text=f"Week of: {timecard.begin_date} - {timecard.end_date}", font_style="Body2")
        heading_box.add_widget(timecard_label)

        entry_column_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.8, None), pos_hint={"center_x": .5, "center_y": .5})
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for entry_column in entry_column_data:
            entry_label = MDLabel(adaptive_height=True, text=entry_column[0], font_style="Body1")
            entry_column_box.add_widget(entry_label)
        heading_box.add_widget(entry_column_box)
        view.add_widget(heading_box)

        days = Service(Day).get({'begin_date': timecard.begin_date})
        days_rows = days if isinstance(days, list) else [days]
        for day in days_rows:
            print(day.weekday)
            weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(0.9, None))
            weekday_label = MDLabel(adaptive_height=True, text=day.weekday, font_style="H6")
            weekday_box.add_widget(weekday_label)

            entries = Service(Entry).get({'dayid': day.dayid})
            if entries:
                entry_rows = entries if isinstance(entries, list) else [entries]
                for entry in entry_rows:
                    entry_row_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.8, None), pos_hint={"center_x": .5, "center_y": .5})
                    entry_rowdata = Utils.data_to_tuple('entry', [entry.as_dict()])
                    print(entry_rowdata)
                    for entry_row in entry_rowdata:
                        for entry_column in entry_row:
                            entry_column_value = entry_column if entry_column else '(active)'
                            entry_label = MDLabel(adaptive_height=True, text=entry_column_value, font_style="Body2")
                            entry_row_box.add_widget(entry_label)
                    weekday_box.add_widget(entry_row_box)

            view.add_widget(weekday_box)

        self.scroller.add_widget(view)

        self.add_widget(self.scroller)

    def edit_task(self, instance):
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
        self.original_values = list(reversed(labels[1:4]))
        self.custom_dialog.content_cls.ids.begin.text = self.original_values[0]
        self.custom_dialog.content_cls.ids.end.text = '' if self.original_values[1] == '(active)' else self.original_values[1] 
        self.custom_dialog.content_cls.ids.code.text = self.original_values[2]

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
