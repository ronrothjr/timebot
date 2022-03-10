class Setting:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.key: str = args[0].get('key')
            self.value: str = args[0].get('value')
            self.active: str = args[0].get('active')
            self.editable: str = args[0].get('editable')
            self.visible: str = args[0].get('visible')
        else:
            self.key: str = args[0]
            self.value: str = args[1]
            self.active: str = args[2]
            self.editable: str = args[3]
            self.visible: str = args[4]

    def as_dict(self):
        items = {'key': self.key, 'value': self.value, 'active': self.active, 'editable': self.editable, 'visible': self.visible}
        return items
