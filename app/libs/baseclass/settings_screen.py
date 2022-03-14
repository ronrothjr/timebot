from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithNoMenu


class TimebotSettingsScreen(MDScreen):

    def __init__(self, **kw):
        super(TimebotSettingsScreen, self).__init__(**kw)
        self.app = App.get_running_app()

    def on_enter(self):
        if not hasattr(self, 'settings_panel'):
            config = ConfigParser()
            my_config = self.app.api.data().load_records('my_config')
            for k, v in my_config.items():
                config.setdefaults(k, v)
            data = self.app.api.data().load_records('config')
            data = self.app.api.data().encode_records(data)
            config.add_callback(self.update_setting)
            s = SettingsWithNoMenu()
            s.add_json_panel('Timebot Settings', config, data=data)
            self.add_widget(s)

    def update_setting(self, *args):
        self.app.api.set_setting(args[2], args[3])
        self.app.api.save_config()
        self.app.api.save_my_config()

