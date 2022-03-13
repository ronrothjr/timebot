class Project:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            self.code = args[0].get('code')
            self.desc = args[0].get('desc')
            self.show = args[0].get('show')
        else:
            print(args)
            self.code = args[0]
            self.desc = args[1]
            self.show = args[2]

    def as_dict(self):
        items = {'code': self.code, 'desc': self.desc, 'show': self.show}
        return items
