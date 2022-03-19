import re
from typing import TypeVar, Generic, List
from db import Sqlite3DB, DatabaseSchema

T = TypeVar('T')

class Repository(Generic[T]):
    
    def __init__(self, object_class: T, database: Sqlite3DB=None, schema: DatabaseSchema=None, setup: bool=False, database_object: Sqlite3DB=None):
        self.object_class = object_class
        self.db: Sqlite3DB = database_object if database_object else database(schema, setup)

    @property
    def name(self):
        original_class = str(self.__orig_class__).lower()
        result = re.search(r"\[(.*?)\]", original_class)
        return result.group(1).split('.')[-1]

    def add(self, t: T) -> int:
        table = self.db.schema.tables[self.name]
        id_model = table.get_id_column()
        column = id_model[0] if id_model else None
        id_value = self.db.add(self.name, t.as_dict())
        if id_value and column and column.type == "INTEGER":
            setattr(t, column.name, id_value)
        return t

    def get(self, query=None):
        records = self.db.get(self.name, query)
        if (isinstance(query, (int, str))):
            return self.object_class(records[query]) if records else None
        else:
            return [self.object_class(r) for r in records.values()]

    def update(self, t: T, update: dict):
        return self.db.update(self.name, t.as_dict(), update)

    def remove(self, id_value=None):
        return self.db.remove(self.name, id_value)