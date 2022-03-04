from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivymd.effects.stiffscroll import StiffScrollEffect
from kivymd.uix.behaviors.elevation import RoundedRectangularElevationBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from service import Service
from project import Project


class TimebotProjectsScreen(MDScreen):

    def on_enter(self):
        self.clear_widgets()
        cards = []
        card_width = int(dp(self.size[0]) * 0.8 / 2)
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.effect_cls = StiffScrollEffect
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}

        view = MDGridLayout(cols=2, padding="10dp", spacing="20dp", adaptive_size=True, size_hint=(0.8, None), pos_hint={"center_x": .5, "center_y": .5})
        projects: List[Project] = Service(Project).get()
        for project in projects:
            project_card = MD3Card(padding=16, radius=[15,], size_hint=(None, None), size=(f'{card_width}dp', "80dp"), line_color=(1, 1, 1, 1))
            cards.append(project_card)
            project_layout = MDRelativeLayout(size=project_card.size, pos_hint={"center_x": .5, "center_y": .5})
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Caption", halign="center", pos_hint={"center_x": .5, "center_y": .5})
            icon_left_pos = project_card.width - (project_card.padding[0] + dp(40))
            icon_top_pos = project_card.height - (project_card.padding[0] + dp(40))
            project_icon = MDIconButton(icon='dots-vertical', pos=(icon_left_pos, icon_top_pos), on_release=self.released)
            project_layout.add_widget(project_label)
            project_layout.add_widget(project_icon)
            project_card.add_widget(project_layout)
            view.add_widget(project_card)

        self.scroller.add_widget(view)
        self.add_widget(self.scroller)



    def released(self, instance):
        print(instance.parent.children[1].text)


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass