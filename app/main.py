import os, sys
from pathlib import Path
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.utils import get_color_from_hex as C 
from libs.baseclass.pre_splash_screen import TimebotPreSplashScreen
from libs.baseclass.root_screen import TimebotRootScreen
from service import Service
from utils import Utils
from setting import Setting
from project import Project
from timecard import Timecard
from day import Day
from task import Task
from api import API
# from kivy.config import Config
# Config.set('graphics', 'width', '370')
# Config.set('graphics', 'height', '760')
# Config.write()

os.environ["DEFAULT_PROJECT_CODE"] = "DRG-403001"

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["TIMEBOT_ROOT"] = sys._MEIPASS
else:
    os.environ["TIMEBOT_ROOT"] = str(Path(__file__).parent)


KV_DIR = f"{os.environ['TIMEBOT_ROOT']}/libs/kv/"

for kv_file in os.listdir(KV_DIR):
    with open(os.path.join(KV_DIR, kv_file), encoding="utf-8") as kv:
        Builder.load_string(kv.read())


class MDTimebot(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window.size = (370, 760)
        Window.softinput_mode = 'below_target'
        self.title = "Timebot"
        self.icon = f"{os.environ['TIMEBOT_ROOT']}/assets/images/logo.png"
        self.services()
        self.utils = Utils

    def services(self):
        self.setting = Service(Setting)
        self.project = Service(Project)
        self.timecard = Service(Timecard)
        self.day = Service(Day)
        self.task = Service(Task)
        API.add_settings()
        os.environ["DEFAULT_PROJECT_CODE"] = API.get_setting('default_project_code').value
        os.environ["UNBILLED_PROJECT_CODE"] = API.get_setting('unbilled_project_code').value
        API.add_current_timecard()

    def callback(self, instance):
        print(instance.icon)

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        FONT_PATH = f"{os.environ['TIMEBOT_ROOT']}/assets/fonts/"

        self.theme_cls.font_styles.update(
            {
                "H1": [FONT_PATH + "RobotoCondensed-Light", 96, False, -1.5],
                "H2": [FONT_PATH + "RobotoCondensed-Light", 60, False, -0.5],
                "H3": [FONT_PATH + "Eczar-Regular", 48, False, 0],
                "H4": [FONT_PATH + "RobotoCondensed-Regular", 34, False, 0.25],
                "H5": [FONT_PATH + "RobotoCondensed-Regular", 24, False, 0],
                "H6": [FONT_PATH + "RobotoCondensed-Bold", 20, False, 0.15],
                "Subtitle1": [
                    FONT_PATH + "RobotoCondensed-Regular",
                    16,
                    False,
                    0.15,
                ],
                "Subtitle2": [
                    FONT_PATH + "RobotoCondensed-Medium",
                    14,
                    False,
                    0.1,
                ],
                "Body1": [FONT_PATH + "Eczar-Regular", 16, False, 0.5],
                "Body2": [FONT_PATH + "RobotoCondensed-Light", 14, False, 0.25],
                "Button": [FONT_PATH + "RobotoCondensed-Bold", 14, True, 1.25],
                "Caption": [
                    FONT_PATH + "RobotoCondensed-Regular",
                    12,
                    False,
                    0.4,
                ],
                "Overline": [
                    FONT_PATH + "RobotoCondensed-Regular",
                    10,
                    True,
                    1.5,
                ],
                "Total": [FONT_PATH + "Eczar-SemiBold", 48, False, 0],
            }
        )
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(TimebotPreSplashScreen(name="timebot splash screen"))
        self.sm.add_widget(TimebotRootScreen(name="timebot root screen"))
        self.sm.current = "timebot splash screen"
        Clock.schedule_once(self.switch, 2)
        return self.sm

    def switch(self, dt):
        self.sm.current = "timebot root screen"


MDTimebot().run()
