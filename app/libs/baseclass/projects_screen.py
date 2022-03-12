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
from task import Task
from api import API


class TimebotAddProjectDialog(MDBoxLayout):
    pass


class TimebotConfirmDeleteProjectDialog(MDBoxLayout):
    pass


class TimebotProjectsScreen(MDScreen):
    custom_dialog = None

    def __init__(self, **kw):
        super(TimebotProjectsScreen, self).__init__(**kw)
        self.scroller = ScrollView()
        self.scroller.bar_width = 0
        self.scroller.size_hint = (0.9, 1)
        self.scroller.pos_hint = {"center_x": .5, "center_y": .5}
        self.view = MDGridLayout(cols=2, padding=dp(10), spacing=dp(20), adaptive_size=True, size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        self.show_projects()
        self.scroller.add_widget(self.view)
        self.add_widget(self.scroller)

    def on_enter(self):
        self.show_projects()

    def show_projects(self):
        self.view.clear_widgets()
        projects: List[Project] = Service(Project).get()
        for project in projects:
            self.add_project_card(project)
        self.add_project_card(Project({'code': 'ADD', 'show': 0}))
    
    def add_project_card(self, project):
        project_card = MD3Card(padding=16, radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(.98, None), size=(dp(120), dp(80)), line_color=(1, 1, 1, 1))
        project_layout = MDRelativeLayout(size=project_card.size, pos_hint={"center_x": .5, "center_y": .5})
        if project.code == 'ADD':
            project_icon_add = MDIconButton(icon='plus', pos_hint={"center_x": .5, "center_y": .5}, on_release=self.released)
            project_layout.add_widget(project_icon_add)
        else:
            project_label = MDLabel(text=project.code, adaptive_width=True, font_style="Body1", halign="center", size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
            project_icon_close = MDIconButton(icon='close', pos_hint={"center_x": .95, "center_y": .9}, on_release=self.confirm_delete_project)
            project_icon_star = MDIconButton(icon='star' if project.show else 'star-outline', pos_hint={"center_x": .95, "center_y": .1}, on_release=self.released)
            project_layout.add_widget(project_label)
            project_layout.add_widget(project_icon_close)
            project_layout.add_widget(project_icon_star)
        project_card.add_widget(project_layout)
        self.view.add_widget(project_card)

    def released(self, instance):
        if instance.icon == 'plus':
            app = App.get_running_app()
            self.custom_dialog = MDDialog(
                title="Add Project Code:",
                type="custom",
                radius=[dp(20), dp(7), dp(20), dp(7)],
                content_cls=TimebotAddProjectDialog(),
                buttons=[
                    MDFlatButton(
                        text="ADD", text_color=app.theme_cls.primary_color,
                        on_release=self.add_project
                    ),
                ],
            )
            self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
            self.custom_dialog.open()
        else:
            print(instance.icon, instance.parent.children[2].text)
            API.toggle_project_code(instance.icon, instance.parent.children[2].text)
            self.show_projects()

    def cancel_dialog(self, *args):
        self.custom_dialog.dismiss(force=True)

    def add_project(self, *args):
        code = self.custom_dialog.content_cls.ids.code.text
        project = Service(Project)
        project.add({'code': code, 'show': 1})
        self.custom_dialog.dismiss(force=True)
        self.show_projects()

    def confirm_delete_project(self, instance):
        print(instance.icon, )
        self.remove_me = instance.parent.children[2].text
        app = App.get_running_app()
        task = Service(Task)
        tasks = task.get({'code': self.remove_me})
        cascade_delete = API.get_setting('cascade_delete').value == '1'
        can_delete = not tasks or tasks and cascade_delete
        button_text = "DELETE" if can_delete else "OK"
        on_release = self.delete_project if can_delete else self.cancel_dialog
        confirm_dialog = TimebotConfirmDeleteProjectDialog()
        self.custom_dialog = MDDialog(
            title="Delete Project",
            type="custom",
            content_cls=confirm_dialog,
            radius=[dp(20), dp(7), dp(20), dp(7)],
            buttons=[
                MDFlatButton(
                    text=button_text, text_color=app.theme_cls.primary_color,
                    on_release=on_release
                ),
            ],
        )
        self.custom_dialog.md_bg_color = app.theme_cls.bg_dark
        if can_delete:
            self.custom_dialog.content_cls.ids.code.text = f'Project: {self.remove_me}'
        else:
            self.custom_dialog.content_cls.ids.error.text = f'{self.remove_me} is used in {len(tasks)} task{"" if len(tasks) == 1 else "s"} and cannot be removed.'
            self.custom_dialog.content_cls.ids.code.text = 'To allow deletion, modify the "Cascade Delete" setting.'
        self.custom_dialog.open()

    def delete_project(self, instance):
        self.custom_dialog.dismiss(force=True)
        
        API.remove_project_code(self.remove_me)
        self.show_projects()

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    pass