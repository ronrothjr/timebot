class Setting:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.key: str = args[0].get('key')
            self.type: str = args[0].get('type')
            self.title: str = args[0].get('title')
            self.value: str = args[0].get('value')
            self.options: str = args[0].get('options')
            self.desc: str = args[0].get('desc')
            self.section: str = args[0].get('section')
        else:
            self.key: str = args[0]
            self.type: str = args[1]
            self.title: str = args[2]
            self.value: str = args[3]
            self.options: str = args[4]
            self.desc: str = args[5]
            self.section: str = args[6]

    def as_dict(self):
        items = {'key': self.key, 'type': self.type, 'title': self.title, 'value': self.value, 'options': self.options, 'desc': self.desc, 'section': self.section}
        return items
