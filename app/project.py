class Project:

    def __init__(self, *args):
        if isinstance(args[0], dict):
            project = args[0]
            self.code = project.get('code')
            self.desc = project.get('desc')
            self.show = project.get('show')
        else:
            self.code = args[0]
            self.desc = args[1]
            self.show = args[2]

    def as_dict(self):
        items = {'code': self.code, 'desc': self.desc, 'show': self.show}
        return items
