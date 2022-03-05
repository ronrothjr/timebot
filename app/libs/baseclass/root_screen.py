from kivymd.uix.screen import MDScreen
from kivy.clock import Clock


class TimebotRootScreen(MDScreen):

    listen = True

    def on_touch_move(self, touch):
        if not self.listen:
            return
        if touch.dx > 50 or touch.dx < -50:
            self.set_tab(touch.dx)

    def set_tab(self, change: int):
        self.listen = False
        def listen_again(target):
            self.listen = True
        Clock.schedule_once(listen_again, 0.3)
        bar = self.ids.nav_bar
        mgr = self.ids.scr_manager
        tabs = [c.text for c in bar.get_buttons()]
        size = len(tabs) - 1
        index = tabs.index(mgr.current)
        if change > 50:
            index += 1 if index < size else -size
        elif change < -50:
            index += -1 if index >= 0 else size
            
        button = bar.get_button(index)
        button.dispatch("on_release")
    
    
        