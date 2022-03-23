from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout


class Orienter(MDBoxLayout):

    def __init__(self, **kw):
        super(Orienter, self).__init__(**kw)
        self.callback = None
        self.orientation = 'vertical'
        self.size = (0.9, 1)
        self.pos_hint = {"center_x": .5, "top": 1}
        self.spacing = dp(10)
        self.orient()

    def set_callback(self, callback):
        self.callback = callback

    def on_size(self, *args):
        self.orient()

    def orient(self):
        if self.width > self.height:
            orientation = 'horizontal'
        else:
            orientation = 'vertical'
        if orientation != self.orientation:
            self.orientation = orientation
            if hasattr(self, 'callback'):
                self.callback(self)