from kivy.utils import get_color_from_hex as gch 
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

    def on_enter(self):
        self.tap = 0
        items = self.parent.parent.children[1].children[0].children
        self.nav_items = [items[3], items[2], items[1], items[0], items[4]]
        self.help_text = [
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
        self.card_view = MDGridLayout(cols=1, size_hint=(None, None), width='300dp', height="160dp", pos_hint={"center_x": .5, "center_y": .20})
        self.add_widget(self.card_view)
        self.next()

    def next(self, *args):
        if len(args) > 0 and args[0].state == 'open':
            self.card_view.clear_widgets()
            Clock.schedule_once(self.show_next, .5)
        else:
            self.card_view.clear_widgets()
            Clock.schedule_once(self.show_next, 1)

    def show_next(self, *args):
        if self.tap < len(self.help_text):
            self.place_card(self.help_text[self.tap]['desc'])
            tap_target_view = MDTapTargetView(
                widget=self.nav_items[self.tap].children[1],
                title_text=self.help_text[self.tap]['title'],
                description_text='tap here to continue',
                widget_position='center',
                title_position=self.help_text[self.tap]['pos'],
                target_circle_color=(0, 0, 0),
                stop_on_target_touch=True,
                stop_on_outer_touch=True
            )
            tap_target_view.bind(on_close=self.next)
            tap_target_view.start()
        self.tap += 1

    def place_card(self, card_text):
        self.card_view.clear_widgets()
        desc_card = MD3Card(padding=16, radius=[15,], size_hint=(None, None), width='300dp', height="160dp", md_bg_color=App.get_running_app().theme_cls.primary_color)
        card_layout = MDRelativeLayout(size_hint=(None, None), width='280dp', height="160dp", pos_hint={"center_x": .5, "center_y": .5})
        card_label = MDLabel(text=card_text, adaptive_height=True, font_style="Subtitle1", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        card_layout.add_widget(card_label)
        desc_card.add_widget(card_layout)
        self.card_view.add_widget(desc_card)

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass
