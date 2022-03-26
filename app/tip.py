class Tip:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.name: str = args[0].get('name')
            self.title: str = args[0].get('title')
            self.desc: str = args[0].get('desc')
            self.card_desc: str = args[0].get(' card_desc')
            self.title_pos: str = args[0].get('title_pos')
            self.widget_pos: str = args[0].get('widget_pos')
            self.version: str = args[0].get('version')
            self.screen: str = args[0].get('screen')
            self.order: int = args[0].get('order')
            self.displayed: str = args[0].get('displayed')
        else:
            self.name: str = args[0]
            self.title: str = args[1]
            self.desc: str = args[2]
            self.card_desc: str = args[3]
            self.title_pos: str = args[4]
            self.widget_pos: str = args[5]
            self.version: str = args[6]
            self.screen: str = args[7]
            self.order: int = args[8]
            self.displayed: str = args[9]

    def as_dict(self):
        items = {
            'name': self.name,
            'title': self.title,
            'desc': self.desc,
            'card_desc': self.card_desc,
            'title_pos': self.title_pos,
            'widget_pos': self.widget_pos,
            'version': self.version,
            'screen': self.screen,
            'order': self.order,
            'displayed': self.displayed
        }
        return items
