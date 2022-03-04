from kivy.metrics import dp
from kivy.utils import get_color_from_hex as gch
from typing import List
from kivy.core.window import Window
from kivy.app import App
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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from service import Service
from project import Project
from api import API


class TimebotAddProjectDialog(MDBoxLayout):
    pass

class TimebotProjectsScreen(MDScreen):
    custom_dialog = None

    def on_enter(self):
        self.clear_widgets()
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.effect_cls = StiffScrollEffect
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}

        self.view = MDGridLayout(cols=2, padding="10dp", spacing="20dp", adaptive_size=True, size_hint=(0.8, None), pos_hint={"center_x": .5, "center_y": .5})
        self.show_projects()
        self.scroller.add_widget(self.view)
        self.add_widget(self.scroller)

    def show_projects(self):
        self.view.clear_widgets()
        projects: List[Project] = Service(Project).get()
        for project in projects:
            self.add_project_card(project)
        self.add_project_card(Project({'code': 'ADD', 'show': 0}))
    
    def add_project_card(self, project):
        project_card = MD3Card(padding=16, radius=[15,], size_hint=(None, None), size=(f'120dp', "80dp"), line_color=(1, 1, 1, 1))
        project_layout = MDRelativeLayout(size=project_card.size, pos_hint={"center_x": .5, "center_y": .5})
        if project.code == 'ADD':
            icon_left_pos = project_card.width / 2 - (project_card.padding[0] + dp(20))
            icon_top_pos = project_card.height / 2 - (project_card.padding[0] + dp(20))
            project_icon_add = MDIconButton(icon='plus', pos=(icon_left_pos, icon_top_pos), on_release=self.released)
            project_layout.add_widget(project_icon_add)
        else:
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Caption", halign="center", pos_hint={"center_x": .5, "center_y": .5})
            icon_left_pos = project_card.width - (project_card.padding[0] + dp(40))
            icon_top_pos = project_card.height - (project_card.padding[0] + dp(40))
            project_icon_close = MDIconButton(icon='close', pos=(icon_left_pos, icon_top_pos), on_release=self.released)
            icon_left_pos = project_card.width - (project_card.padding[0] + dp(40))
            icon_top_pos = project_card.height - (project_card.padding[0] + dp(85))
            project_icon_star = MDIconButton(icon='star' if project.show else 'star-outline', pos=(icon_left_pos, icon_top_pos), on_release=self.released)
            project_layout.add_widget(project_label)
            project_layout.add_widget(project_icon_close)
            project_layout.add_widget(project_icon_star)
        project_card.add_widget(project_layout)
        self.view.add_widget(project_card)


    def released(self, instance):
        if instance.icon == 'plus':
            print(instance.icon)
            self.custom_dialog = MDDialog(
                title="Add Project Code:",
                type="custom",
                content_cls=TimebotAddProjectDialog(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        text_color=App.get_running_app().theme_cls.primary_color,
                        on_release=self.cancel_dialog
                    ),
                    MDFlatButton(
                        text="OK", text_color=App.get_running_app().theme_cls.primary_color,
                        on_release=self.add_project
                    ),
                ],
            )
            self.custom_dialog.md_bg_color = App.get_running_app().theme_cls.bg_dark
            self.custom_dialog.open()
        else:
            print(instance.icon, instance.parent.children[2].text)
            API.remove_or_toggle_project_code(instance.icon, instance.parent.children[2].text)
            self.show_projects()

    def cancel_dialog(self, *args):
        self.custom_dialog.dismiss(force=True)

    def add_project(self, *args):
        code = self.custom_dialog.content_cls.ids.code.text
        project = Service(Project)
        project.add({'code': code, 'show': 1})
        self.custom_dialog.dismiss(force=True)
        self.show_projects()

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass