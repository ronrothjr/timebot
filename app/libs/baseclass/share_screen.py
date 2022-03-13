from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.uix.screen import MDScreen
from kivy.uix.modalview import ModalView
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast

class TimebotShareScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.manager = None
        box = BoxLayout(orientation= 'vertical',
    spacing= dp(5))
        float_latout = FloatLayout()
        button_box = MDRoundFlatIconButton(
            text="Open manager",
            icon="folder",
            pos_hint={'center_x': .5, 'center_y': .6},
            on_release=self.file_manager_open
        )
        float_latout.add_widget(button_box)
        box.add_widget(float_latout)
        self.add_widget(box)

    def file_manager_open(self, *args):
        if not hasattr(self, 'modal'):
            toast(StoragePath().get_downloads_dir())
            self.modal = ModalView(size_hint=(1, .8), auto_dismiss=False)
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager, select_path=self.select_path)
            self.modal.add_widget(self.file_manager)
            self.file_manager.show('/')  # output manager to the screen
        self.modal_open = True
        Window.bind(on_keyboard=self.events)
        self.modal.open()

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        toast(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        Window.unbind(on_keyboard=self.events)
        self.modal.dismiss()
        self.modal_open = False

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device..'''
        try:
            if keyboard in (1001, 27):
                if self.modal_open:
                    self.file_manager.back()
            return True
        except:
            "do nothing"