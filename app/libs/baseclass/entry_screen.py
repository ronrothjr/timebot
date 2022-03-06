from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.effects.stiffscroll import StiffScrollEffect
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRoundFlatButton
from service import Service
from project import Project
from day import Day
from entry import Entry
from utils import Utils
from api import API


class TimebotEntryScreen(MDScreen):

    def on_enter(self):
        self.clear_widgets()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        # self.scroller.effect_cls = StiffScrollEffect
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}

        view = MDList(spacing=dp(10))

        grid = MDGridLayout(cols=2, padding="10dp", spacing="20dp", adaptive_size=True, size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})

        projects: List[Project] = Service(Project).get({'show': 1})
        for project in projects:
            project_card = MD3Card(padding=16, radius=[15,], size_hint=(1, None), size=('120dp', "80dp"), line_color=(1, 1, 1, 1), on_release=self.released)
            project_layout = MDRelativeLayout(size=project_card.size, pos_hint={"center_x": .5, "center_y": .5})
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Caption", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
            project_layout.add_widget(project_label)
            project_card.add_widget(project_layout)
            grid.add_widget(project_card)

        view.add_widget(grid)

        self.list_view = MDList(spacing=dp(10))
        self.show_today()
        view.add_widget(self.list_view)

        self.scroller.add_widget(view)
        self.add_widget(self.scroller)

    def show_today(self):
        self.list_view.clear_widgets()

        today, begin_date, weekday = Utils.get_begin_date()
        day = Service(Day).get({'begin_date': begin_date, 'weekday': weekday})[0]
        entries = Service(Entry).get({'dayid': day.dayid})
        if not entries:
            empty_card = MD3Card(padding=16, radius=[15,], size_hint=(.98, None), size=('120dp', "80dp"), md_bg_color=gch('606060'), line_color=(1, 1, 1, 1))
            empty_layout = MDRelativeLayout(size=empty_card.size, pos_hint={"center_x": .5, "center_y": .5})
            empty_label = MDLabel(text="You have no tasks for today", adaptive_width=True, font_style="Caption", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
            empty_layout.add_widget(empty_label)
            empty_card.add_widget(empty_layout)
            self.list_view.add_widget(empty_card)
        else:
            weekday_box = MDBoxLayout(adaptive_height=True, orientation='vertical', size_hint=(0.9, None))
            weekday_label = MDLabel(adaptive_height=True, text=day.weekday, font_style="H6")
            weekday_box.add_widget(weekday_label)
        
            entry_column_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.9, None), pos_hint={"center_x": .6, "center_y": .5})
            entry_column_data = Utils.schema_dict_to_tuple('entry')
            for entry_column in entry_column_data:
                entry_label = MDLabel(adaptive_height=True, text=entry_column[0], pos_hint={"center_x": .5, "center_y": .5}, font_style="Body1")
                entry_column_box.add_widget(entry_label)
            entry_label = MDLabel(adaptive_height=True, text="", font_style="Body1")
            entry_column_box.add_widget(entry_label)
            weekday_box.add_widget(entry_column_box)

            entry_rows = entries if isinstance(entries, list) else [entries]
            for entry in entry_rows:
                entry_row_box = MDBoxLayout(adaptive_height=True, orientation='horizontal', size_hint=(0.9, None), pos_hint={"center_x": .6, "center_y": .5})
                entry_rowdata = Utils.data_to_tuple('entry', [entry.as_dict()])
                print(entry_rowdata)
                for entry_row in entry_rowdata:
                    for entry_column in entry_row:
                        entry_column_value = entry_column if entry_column else '(In progress)'
                        entry_label = MDLabel(text=entry_column_value, size_hint=(.5, None), pos_hint={"center_x": .5, "center_y": .5}, font_style="Body2")
                        entry_row_box.add_widget(entry_label)
                    entry_delete = MDIconButton(icon="close", user_font_size="14sp", on_release=self.delete_entry)
                    entry_row_box.add_widget(entry_delete)
                weekday_box.add_widget(entry_row_box)

            last_entry = API.get_last_entry()
            if last_entry and not last_entry.end:
                widget_spacer = Widget(size_hint_y=None, height="10dp")
                weekday_box.add_widget(widget_spacer)
                end_task_button = MDRoundFlatButton(text="End Current Task", on_release=self.end_task, pos_hint={"center_x": .5, "center_y": .5}, line_color=gch('ffffff'))
                weekday_box.add_widget(end_task_button)

            self.list_view.add_widget(weekday_box)

    def released(self, instance):
        API.switch_or_start_task(instance.children[0].children[0].text)
        self.show_today()

    def delete_entry(self, instance):
        labels = [c.text for c in instance.parent.children]
        API.remove_task(*labels)
        self.show_today()

    def end_task(self, instance):
        API.switch_or_start_task()
        self.show_today()


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass