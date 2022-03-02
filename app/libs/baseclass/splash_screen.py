from kivymd.uix.screen import MDScreen
from kivy.clock import Clock


class TimebotSplashScreen(MDScreen):

    def on_enter(self, *args):
        Clock.schedule_once(self.skip, 2)

    def skip(self, dt):
        self.parent.parent.parent.parent.current = "timebot root screen"
