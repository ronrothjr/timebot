from calendar import week
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.effects.stiffscroll import StiffScrollEffect
from kivy.app import App
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label import MDLabel
from pyparsing import col
from service import Service
from day import Day
from timecard import Timecard
from entry import Entry
from utils import Utils


class TimebotTimecardsScreen(MDScreen):
    def on_enter(self):
        scroller = ScrollView()
        scroller.bar_width = 0
        scroller.effect_cls = StiffScrollEffect
        scroller.size_hint = (0.9, 0.9)
        scroller.pos_hint = {"center_x": .5, "center_y": .5}
        
        view = MDList(spacing=dp(10))

        timecard: Timecard = Service(Timecard).get()[0]

        timecard_label = MDLabel(adaptive_height=True, text=f"Timecard: {timecard.begin_date} - {timecard.end_date}", font_style="Body2")

        view.add_widget(timecard_label)


        days = Service(Day).get({'begin_date': timecard.begin_date})
        days_rows = days if isinstance(days, list) else [days]
        
        entry_column_data = Utils.schema_dict_to_tuple('entry')
        for day in days_rows:
            print(day.weekday)
            weekday_label = MDLabel(adaptive_height=True, text=day.weekday, font_style="H4")
            view.add_widget(weekday_label)
            entry_column_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.9, None))
            for entry_column in entry_column_data:
                entry_label = MDLabel(adaptive_height=True, text=entry_column[0], font_style="Body1")
                entry_column_box.add_widget(entry_label)
            view.add_widget(entry_column_box)
            
            entries = Service(Entry).get({'dayid': day.dayid})
            if entries:
                entry_rows = entries if isinstance(entries, list) else [entries]
                for entry in entry_rows:
                    entry_row_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.9, None))
                    entry_rowdata = Utils.data_to_tuple('entry', [entry.as_dict()])
                    print(entry_rowdata)
                    for entry_row in entry_rowdata:
                        for entry_column in entry_row:
                            entry_label = MDLabel(adaptive_height=True, text=entry_column, font_style="Body2")
                            entry_row_box.add_widget(entry_label)
                    view.add_widget(entry_row_box)        

        scroller.add_widget(view)

        self.add_widget(scroller)

    def scroll_view(self):
        return Widget()

    def get_label(self, text: str, font_style: str) -> MDLabel:
        return MDLabel(adaptive_height=True, text=text, font_style=font_style)
