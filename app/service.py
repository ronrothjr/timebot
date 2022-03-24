import os
from repository import Repository
from db import Sqlite3DB, DatabaseSchema
from utils import Utils


class Service:

    def __init__(self, object_class, database: Sqlite3DB=None, schema_dict=None, setup: bool=False):
        schema = DatabaseSchema(**Utils.get_schema() if not schema_dict else schema_dict)
        db = database if database else Sqlite3DB
        self.object_class = object_class
        self.repository = Repository[object_class](object_class=object_class, database=db, schema=schema, setup=setup)

    def add(self, *args):
        obj = self.object_class(*args)
        result = self.repository.add(obj)
        Utils.backup_db(os.environ.get('TIMEBOT_ROOT', None))
        return result

    def get(self, query=None):
        result = self.repository.get(query)
        return result

    def update(self, obj, data):
        result = self.repository.update(obj, data)
        Utils.backup_db(os.environ.get('TIMEBOT_ROOT', None))
        return result

    def remove(self, id_value=None):
        result = self.repository.remove(id_value)
        Utils.backup_db(os.environ.get('TIMEBOT_ROOT', None))
        return result