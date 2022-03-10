from kivymd.uix.screen import MDScreen
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithNoMenu
from api import API


class TimebotSettingsScreen(MDScreen):

    def on_enter(self):
        if not hasattr(self, 'settings_panel'):
            config = ConfigParser()
            my_config = API.data().load_records('my_config')
            print(my_config)
            for k, v in my_config.items():
                config.setdefaults(k, v)
            data = API.data().load_records('config')
            data = API.data().encode_records(data)
            print(data)

            s = SettingsWithNoMenu()
            s.add_json_panel('Timebot Settings', config, data=data)
            self.add_widget(s)