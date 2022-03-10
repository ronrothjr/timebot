from kivymd.uix.screen import MDScreen
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithNoMenu
from api import API


class TimebotSettingsScreen(MDScreen):

    def on_enter(self):
        if not hasattr(self, 'settings_panel'):
            config = ConfigParser()
            my_config = API.data().load_records('my_config')
            for k, v in my_config.items():
                config.setdefaults(k, v)
            data = API.data().load_records('config')
            data = API.data().encode_records(data)
            config.add_callback(self.update_setting)
            s = SettingsWithNoMenu()
            s.add_json_panel('Timebot Settings', config, data=data)
            self.add_widget(s)

    def update_setting(*args):
        API.set_setting(args[2], args[3])
        API.save_config()
        API.save_my_config()

