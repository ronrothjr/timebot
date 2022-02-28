import sqlite3, datetime


class DB:

    def __init__(self, db_name: str, tables: dict):
        self.db_name = db_name
        self.tables = tables
        self.now = f"'{str(datetime.datetime.now())}'"
        for name, fields in tables.items():
            self.create(name, fields)

    def create(self, name: str, fields: dict):
        fields_str, fields = self.get_field_definitions(name, fields)
        self.tables[name] = fields
        sql = f'CREATE TABLE if not exists {name} ({fields_str})'
        self.execute(sql)

    def get_field_definitions(self, name: str, fields: dict):
        new_fields = {}
        if not self.get_id_field_dict(fields):
            new_fields[f'{name}id'] = {'name': f'{name}id', 'type': 'INTEGER', 'id': True}
        for name, f in fields.items():
            new_fields[name] = f
        if not 'create_timestamp' in fields:
            new_fields['create_timestamp'] ={'name': 'create_timestamp', 'type': 'TEXT'}
        if not 'last_update_timestamp' in fields:
            new_fields['last_update_timestamp'] ={'name': 'last_update_timestamp', 'type': 'TEXT'}
        field_list = []
        for name, f in new_fields.items():
            field = f'{name} {f["type"]}'
            field += " PRIMARY KEY" if "id" in f and f["id"] else ''
            field += f" REFERENCES {f['ref']}" if 'ref' in f else ''
            field += f" ON UPDATE CASCADE ON DELETE CASCADE" if 'trigger' in f and f['trigger'] == 'CASCADE' else ''
            field_list.append(field)
        fields_str = ','.join(field_list)
        return fields_str, new_fields

    def get_field_value(self, table_name: str, field: dict, data: dict):
        value = None
        if 'id' in field and field['id'] and field['type'] == 'INTEGER':
            records = self.get(table_name)
            id_field = self.get_id_field(self.tables[table_name])
            max_id = max(records.values(), key=lambda x:x[id_field])[id_field] if records else 0
            value = f"{max_id + 1}"
        elif '_timestamp' in field['name']:
            value = f"'{self.now}'"
        else:
            value = f"'{data[field['name']]}'"
        return value

    def get_id_field(self, fields: dict):
        id_field_dict = self.get_id_field_dict(fields)
        id = id_field_dict[0]['name'] if id_field_dict else None
        return id

    def get_id_field_dict(self, fields: dict):
        id_field = list(filter(lambda x: 'id' in x and x['id'], fields.values()))
        return id_field

    def get_id_field_value(self, fields: dict, data: dict):
        id = self.get_id_field(fields)
        id_value = data[id] if id in data else None
        return id, id_value

    def add(self, table_name: str, data: dict):
        self.now = str(datetime.datetime.now())
        fields = self.tables[table_name]
        values = ','.join([self.get_field_value(table_name, f, data) for f in fields.values()])
        self.execute("INSERT INTO {} VALUES ({})".format(table_name, values))

    def get(self, table_name, id_value: int=None):
        fields = self.tables[table_name]
        id_field = self.get_id_field(fields)
        sql_id_value = (id_value if isinstance(id_value, int) else f"'{id_value}'") if id_value else ''
        where = f" WHERE {id_field} = {sql_id_value}" if id_value else ''
        results = self.execute(f"SELECT * from {table_name}{where}", fetch=True)
        records = {}
        for r in results:
            record = {}
            for x in range(0, len(fields.keys())):
                name = list(fields.keys())[x]
                record[name] = r[x]
            id, id_value = self.get_id_field_value(fields, record)
            records[id_value] = record
        return records

    def update(self, table_name: str, data: dict, update: dict):
        self.now = str(datetime.datetime.now())
        fields = self.tables[table_name]
        id_field = self.get_id_field(fields)
        id_value = data[id_field] if id_field else None
        record = self.get(table_name, id_value)
        if id_field and record:
            updates = []
            for k, v in update.items():
                field = list(filter(lambda x: x['name'] == k, fields.values()))
                if field and k not in ['create_timestamp']:
                    value = v
                    if k == 'last_update_timestamp':
                        value = self.now
                    if not field[0]['type'] == 'INTEGER':
                        value = f"'{value}'"
                    updates.append(f"{k} = {value}")
            updates_str = ', '.join(updates)
            sql_id_value = (id_value if isinstance(id_value, int) else f"'{id_value}'") if id_value else ''
            self.execute(f"UPDATE {table_name} SET {updates_str} WHERE {id_field} = {sql_id_value}")

    def remove(self, table_name, id_value=None):
        where = ''
        if id_value:
            fields = self.tables[table_name]
            id_field = self.get_id_field(fields)
            sql_id_value = (id_value if isinstance(id_value, int) else f"'{id_value}'") if id_value else ''
            where = f' WHERE {id_field} = {sql_id_value}'
        self.execute(f"DELETE FROM {table_name}{where}")

    def execute(self, sql, fetch:bool=False):
        records = None
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        c.execute('BEGIN;')
        try:
            c.execute(sql)
            if fetch:
                records = c.fetchall()
            c.execute('COMMIT;')
        except Exception as e:
            print(e)
            c.execute('ROLLBACK;')
        conn.commit()
        conn.close()
        if fetch:
            return records