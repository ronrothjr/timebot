from db import DB, DatabaseSchema


class Repository:
    
    def __init__(self, DB: DB, schema: DatabaseSchema):
        self.db = DB(schema)
