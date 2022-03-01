class Project:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.code = args[0].get('code')
        else:
            self.code = args[0]

    def as_dict(self):
        items = {'code': self.code}
        return items