from repository import Repository
from db import Sqlite3DB, DatabaseSchema
from utils import Utils


class Service:

    def __init__(self, object_class, database: Sqlite3DB=None, schema_dict=None):
        schema = DatabaseSchema(**Utils.get_schema() if not schema_dict else schema_dict)
        db = database if database else Sqlite3DB
        self.object_class = object_class
        self.repository = Repository[object_class](object_class, db, schema)

    def add(self, *args):
        obj = self.object_class(*args)
        return self.repository.add(obj)

    def get(self, query=None):
        return self.repository.get(query)

    def update(self, obj, data):
        return self.repository.update(obj, data)

    def remove(self, id_value=None):
        return self.repository.remove(id_value)