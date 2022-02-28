import sqlite3, datetime


class DB:

    def __init__(self, db_name: str, tables: dict):
        self.db_name = db_name
        self.tables = tables
        for name, fields in tables.items():
            self.create(name, fields)

    def create(self, name: str, fields: list):
        field_list = ','.join([f'{f["name"]} {f["type"]}' for f in fields])
        sql = f'CREATE TABLE if not exists {name} ({field_list}, timestamp text)'
        self.execute(sql)

    def add(self, table_name: str, data: dict):
        fields = self.tables[table_name]
        values = ','.join([f"'{data[f['name']]}'" for f in fields] + [f"'{str(datetime.datetime.now())}'"])
        self.execute("INSERT INTO {} VALUES ({})".format(table_name, values))

    def get(self, table_name):
        results = self.execute(f"SELECT * from {table_name}", fetch=True)
        fields = self.tables[table_name]
        records = []
        for r in results:
            record = {}
            for x in range(0, len(fields)):
                record[fields[x]['name']] = r[x]
            record['timestamp'] = r[len(fields)]
            records.append(record)
        return records

    def remove(self, table_name:str, id:int=None):
        self.execute(f"DELETE FROM {table_name}{' id=' + str(id) if id else ''}")

    def execute(self, sql, fetch:bool=False):
        records = None
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(sql)
        if fetch:
            records = c.fetchall()
        conn.commit()
        conn.close()
        if fetch:
            return records