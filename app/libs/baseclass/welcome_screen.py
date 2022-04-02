import os, pydash
from kivy.utils import get_color_from_hex as gch 
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from .orienter import Orienter
from .piechart import AKPieChart, AKBarChart


class Barchart:
    pass


class TimebotWelcomeScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotWelcomeScreen, self).__init__(**kw)
        self.app = App.get_running_app()
        self.top_center = {"center_x": .5, "top": 1}
        self.orienter = Orienter()
        self.add_pie_chart_box()
        self.add_bar_chart_box()
        self.setup_tour()
        self.add_widget(self.orienter)
        self.orienter.set_callback(self.orient)
        self.orienter.orient()

    def orient(self, orienter):
        pass
#        if orienter.orientation == 'vertical':
#            self.pie_chart_box.size_hint_y = None
#            self.bar_chart_box.size_hint_y = None
#        else:
#            self.pie_chart_box.size_hint_y = 1
#            self.bar_chart_box.size_hint_y = 1

    def on_enter(self):
        self.pie_chart_box.clear_widgets()
        self.bar_chart_box.clear_widgets()
        self.add_piechart()
        self.add_barchart()
        self.take_tour()

    def refresh(self):
        self.pie_chart_box.clear_widgets()
        self.add_piechart()
        self.bar_chart_box.clear_widgets()
        self.add_barchart()

    def add_pie_chart_box(self):
        chart_view = MDBoxLayout(orientation="vertical", pos_hint=self.top_center)
        chart_title = MDLabel(text='This Week', font_style="H6", size_hint=(1, 1), height=dp(50), halign="center", pos_hint=self.top_center)
        chart_view.add_widget(chart_title)
        self.pie_chart_box = MDBoxLayout(
            adaptive_height=True,
            padding=dp(24),
            orientation="vertical"
        )
        chart_view.add_widget(self.pie_chart_box)
        self.orienter.add_widget(chart_view)

    def add_piechart(self):
        items = self.get_piechart_items()
        if not items:
            items = {'no billable tasks': 100}
        piechart = AKPieChart(
            items=[items],
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=[None, None],
            size=(dp(280), dp(280)),
            color_palette="Green"
        )
        self.pie_chart_box.add_widget(piechart)

    def get_piechart_items(self):
        today, begin_date, weekday = self.app.utils.get_begin_date()
        self.timecard = self.app.timecard.get(begin_date)
        self.days = self.app.day.get({'begin_date': self.timecard.begin_date})
        dayids = [day.dayid for day in self.days]
        tasks = [t.as_dict() for t in self.app.task.get({'dayid': dayids})] if dayids else []
        data_rows = self.app.utils.data_to_dict('task', tasks) if tasks else []
        totals = {}
        for d in data_rows:
            if d['code'] != os.environ["UNBILLED_PROJECT_CODE"]:
                t = d['total'].split(':')
                total = ( int(t[0]) * 60 ) + int(t[1])
                if d['code'] not in totals:
                    totals[d['code']] = 0
                totals[d['code']] += total
        total = 0
        for t in totals.values():
            total += t
        items = {}
        for k, v in totals.items():
            items[k] = float("{:.4f}".format(v / total)) * 100
        total = 0.0
        for t in items.values():
            total += t
        if items:
            items[list(items.keys())[0]] += 100.0 - total
        return items

    def add_bar_chart_box(self):
        chart_view = MDBoxLayout(orientation="vertical", pos_hint=self.top_center)
        chart_title = MDLabel(text='Weekly Totals', font_style="H6", size_hint=(1, 1), height=dp(50), halign="center", pos_hint=self.top_center)
        chart_view.add_widget(chart_title)
        self.bar_chart_box = MDBoxLayout(
            adaptive_height=True,
            padding=dp(24),
            orientation="vertical"
        )
        chart_view.add_widget(self.bar_chart_box)
        self.orienter.add_widget(chart_view)

    def add_barchart(self):
        v = self.get_barchart_values()
        barchart = AKBarChart(
            size_hint_y=None,
            height=dp(240),
            x_values=v['x_values'],
            y_values=v['y_values'],
            label_size=dp(16),
            labels=True,
            anim=True,
            x_labels=v['x_labels'],
            bars_color=(.2, .2, .2, 1),
            labels_color=(.2, .2, .2, 1),
            lines_color=(.3, .3, .3, 1)
        )
        self.bar_chart_box.add_widget(barchart)

    def get_barchart_values(self):
        v = {
            'x_values': [],
            'y_values': [],
            'x_labels': []
        }
        timecards = self.app.timecard.get()[-5:]
        for t in timecards:
            total = self.get_timecard_total(t)
            v['x_values'].append(total)
            v['y_values'].append(total)
            v['x_labels'].append(str(t.begin_date)[-5:])
        return v

    def get_timecard_total(self, t):
        self.days = self.app.day.get({'begin_date': t.begin_date})
        dayids = [day.dayid for day in self.days]
        tasks = [t.as_dict() for t in self.app.task.get({'dayid': dayids})] if dayids else []
        data_rows = self.app.utils.data_to_dict('task', tasks) if tasks else []
        total = 0
        for d in data_rows:
            if d['code'] != os.environ["UNBILLED_PROJECT_CODE"]:
                t = d['total'].split(':')
                total += ( int(t[0]) * 60 ) + int(t[1])
        return float("{:.1f}".format(total / 60))

    def setup_tour(self):
        self.tap = 0
        self.tap_text = {
            '0.0.0': [
                {
                    'name': 'entry_tip',
                    'title': 'This is the Today screen',
                    'desc': None,
                    'card_desc': 'Go here to record and edit tasks for today',
                    'widget_pos': 'center',
                    'title_pos': 'bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 1
                },
                {
                    'name': 'timecards_tip',
                    'title': 'This is the Timecards screen',
                    'desc': None,
                    'card_desc': 'This will display the current timecard week, so you can review and edit the tasks before submission',
                    'widget_pos': 'center',
                    'title_pos': 'left_bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 2
                },
                {
                    'name': 'projects_tip',
                    'title': 'This is the Projects screen',
                    'desc': None,
                    'card_desc': 'Here you can manage your list of projects available on the Entry screen',
                    'widget_pos': 'center',
                    'title_pos': 'left_bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 3
                },
                {
                    'name': 'undo_tip',
                    'title': 'This is the Undo button',
                    'desc': None,
                    'card_desc': 'You can restore your timesheets to a previous point in time',
                    'widget_pos': 'center',
                    'title_pos': 'left_bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 4
                },
                {
                    'name': 'settings_tip',
                    'title': 'This is the Settings screen',
                    'desc': None,
                    'card_desc': 'You have various ways to control the actions of Timebot, like setting which Project Code to automatically add to blank timesheets',
                    'widget_pos': 'center',
                    'title_pos': 'left_bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 5
                },
                {
                    'name': 'welcome_tip',
                    'title': 'This is the Welcome screen',
                    'desc': None,
                    'card_desc': 'Updates to the application and other data will show here in this screen',
                    'widget_pos': 'center',
                    'title_pos': 'right_bottom',
                    'version': '0.0.0',
                    'screen': 'welcome',
                    'order': 6
                }
            ]
        }
        self.tour_setting = self.app.api.get_setting('version_tour')
        self.tour = self.tour_setting.value

    def take_tour(self):
        if self.tour == '0.0.0':
            self.take_tour_0_0_0()
            options = self.tour_setting.options.split(',')
            tour_index = options.index(self.tour)
            next_version = options[tour_index - 1] if tour_index - 1 > 0 else None
            if next_version:
                self.app.api.set_setting('version_tour', next_version)

    def take_tour_0_0_0(self):
        print(pydash.get(self, 'parent.parent.children[1].children[0].children'))
        items = self.parent.parent.children[1].children[0].children
        self.tap_items = [items[4], items[3], items[2], items[1], items[0], items[5]]
        self.card_view = MDGridLayout(cols=1, size_hint=(None, None), width=dp(300), height=dp(160), pos_hint={"center_x": .5, "center_y": .20})
        self.add_widget(self.card_view)
        Clock.schedule_once(self.next_0_0_0, 2)

    def next_0_0_0(self, *args):
        if isinstance(args, tuple) and len(args) > 0 and not isinstance(args[0], float) and args[0].state == 'open':
            self.card_view.clear_widgets()
            Clock.schedule_once(self.show_next_0_0_0, .5)
        else:
            self.card_view.clear_widgets()
            Clock.schedule_once(self.show_next_0_0_0, 1)

    def show_next_0_0_0(self, *args):
        if self.tap < len(self.tap_text[self.tour]):
            tip = self.tap_text[self.tour][self.tap]
            if tip['card_desc']:
                self.place_card(tip['card_desc'])
            tap_settings = {
                'widget': self.tap_items[self.tap].children[1],
                'title_text': tip['title'],
                'description_text': tip['desc'] if tip['desc'] else 'tap here to continue',
                'widget_position': tip['widget_pos'],
                'title_position': tip['title_pos'],
                'target_circle_color': (0, 0, 0),
                'stop_on_target_touch': True,
                'stop_on_outer_touch': True
            }
            tap_target_view = MDTapTargetView(**tap_settings)
            tap_target_view.bind(on_close=self.next_0_0_0)
            tap_target_view.start()
        self.tap += 1

    def place_card(self, card_text):
        self.card_view.clear_widgets()
        desc_card = MD3Card(padding=dp(16), radius=[dp(15),], size_hint=(None, None), width=dp(300), height=dp(160), md_bg_color=self.app.theme_cls.primary_color)
        card_layout = MDRelativeLayout(size_hint=(None, None), width=dp(280), height=dp(160), pos_hint={"center_x": .5, "center_y": .5})
        card_label = MDLabel(text=card_text, adaptive_height=True, font_style="Subtitle1", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        card_layout.add_widget(card_label)
        desc_card.add_widget(card_layout)
        self.card_view.add_widget(desc_card)

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass
