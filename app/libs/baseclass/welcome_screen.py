from kivy.utils import get_color_from_hex as gch 
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior


class TimebotWelcomeScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotWelcomeScreen, self).__init__(**kw)
        self.app = App.get_running_app()
        self.tap = 0
        self.tap_text = {
            '0.0.0': [
                {
                    'title': 'This is the Entry screen',
                    'desc': 'Go here to record and edit tasks for today',
                    'pos': 'bottom'
                },
                {
                    'title': 'This is the Projects screen',
                    'desc': 'Here you can manage your list of projects available on the Entry screen',
                    'pos': 'left_bottom'
                },
                {
                    'title': 'This is the Timecards screen',
                    'desc': 'This will display the current timecard week, so you can review and edit the tasks before submission',
                    'pos': 'left_bottom'
                },
                {
                    'title': 'This is the Share screen',
                    'desc': 'You can export your timesheet and send it along to your chosen external application',
                    'pos': 'left_bottom'
                },
                {
                    'title': 'This is the Settings screen',
                    'desc': 'You have various ways to control the actions of Timebot, like setting which Project Code to automatically add to blank timesheets',
                    'pos': 'left_bottom'
                },
                {
                    'title': 'This is the Welcome screen',
                    'desc': 'Updates to the application and other data will show here in this screen',
                    'pos': 'right_bottom'
                }
            ]
        }
        self.tour_setting = self.app.api.get_setting('version_tour')
        self.tour = self.tour_setting.value
        print(self.tour)

    def on_enter(self):
        if self.tour == '0.0.0':
            self.take_tour_0_0_0()
            options = self.tour_setting.options.split(',')
            tour_index = options.index(self.tour)
            next_version = options[tour_index - 1] if tour_index - 1 > 0 else None
            if next_version:
                self.app.api.set_setting('version_tour', next_version)

    def take_tour_0_0_0(self):
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
            self.place_card(self.tap_text[self.tour][self.tap]['desc'])
            tap_target_view = MDTapTargetView(
                widget=self.tap_items[self.tap].children[1],
                title_text=self.tap_text[self.tour][self.tap]['title'],
                description_text='tap here to continue',
                widget_position='center',
                title_position=self.tap_text[self.tour][self.tap]['pos'],
                target_circle_color=(0, 0, 0),
                stop_on_target_touch=True,
                stop_on_outer_touch=True
            )
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
