class Project:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.code = args[0].get('code')
            self.show = args[0].get('show')
        else:
            self.code = args[0]
            self.show = args[1]

    def as_dict(self):
        items = {'code': self.code, 'show': self.show}
        return items
