import os, sqlite3, datetime
from typing import Dict, List, Union


class DatabaseSchema:

    def __init__(self, db_name: str, tables: dict):
        self.db_name = db_name
        self.tables: Dict[str, Table] = self.get_schema(tables)

    def get_schema(self, tables: dict):
        schema = {}
        for name, fields in tables.items():
            schema[name] = Table(name, fields)
        return schema


class Column:

    def __init__(self, field: dict):
        self.name: str = field.get('name')
        self.type: str = field.get('type')
        self.id: bool = field.get('id', False)
        self.calc: str = field.get('calc', None)
        self.ref: str = field.get('ref', '')
        self.trigger: str = field.get('trigger', '')


class Table:

    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = self.get_field_definitions(fields)
        self.model: Dict[str, Column] = self.get_model()
        self.create: str = self.get_create_sql()
        self.drop: str = self.get_drop_sql()

    @property
    def now(self):
        return str(datetime.datetime.now())

    def get_field_definitions(self, fields: dict):
        new_fields = {}
        id_field = list(filter(lambda x: 'id' in x and x['id'], fields.values()))
        if not id_field:
            new_fields[f'{self.name}id'] = {'name': f'{self.name}id', 'type': 'INTEGER', 'id': True, 'dp': 10}
        for name, f in fields.items():
            if f.get('type')in ['TEXT', 'INTEGER']:
                new_fields[name] = f
        if not 'create_timestamp' in fields:
            new_fields['create_timestamp'] ={'name': 'create_timestamp', 'type': 'TEXT'}
        if not 'last_update_timestamp' in fields:
            new_fields['last_update_timestamp'] ={'name': 'last_update_timestamp', 'type': 'TEXT'}
        return new_fields

    def get_model(self) -> dict:
        model = {}
        for name, props in self.fields.items():
            if props['type'] in ['TEXT', 'INTEGER']:
                model[name] = Column(props)
        return model

    def get_create_sql(self) -> str:
        column_list = []
        for name, m in self.model.items():
            column = f'{name} {m.type}'
            column += " PRIMARY KEY" if m.id else ''
            column += f" REFERENCES {m.ref}" if m.ref else ''
            column += f" ON UPDATE CASCADE ON DELETE CASCADE" if m.trigger == 'CASCADE' else ''
            column_list.append(column)
        table_str = ','.join(column_list)
        sql = f'CREATE TABLE if not exists {self.name} ({table_str})'
        return sql

    def get_drop_sql(self) -> str:
        sql = f'DROP TABLE if exists {self.name}'

    def get_id_name(self):
        id_model = self.get_id_column()
        id = id_model[0].name if id_model else None
        return id

    def get_id_column(self) -> List[Column]:
        columns = list(self.model.values())
        id_model = list(filter(lambda c: c.id, columns))
        return id_model

    def get_id_field_value(self, data: dict):
        id = self.get_id_name()
        id_value = data[id] if id in data else None
        return id, id_value

    def get_column_value(self, column: Column, data: dict, max_id):
        value = None
        if column.id and column.type == 'INTEGER':
            value = f"{max_id + 1}"
        elif '_timestamp' in column.name:
            value = f"'{self.now}'"
        elif data.get(column.name) is None:
            value = 'null'
        else:
            value = f"'{data[column.name]}'"
        return value


class Sqlite3DB:

    def __init__(self, schema: DatabaseSchema, setup: bool=False):
        self.schema = schema
        self.now = f"'{str(datetime.datetime.now())}'"
        self.conn = sqlite3.connect(self.schema.db_name)
        self.results = None
        [self.execute(table.create) for table in schema.tables.values() if setup]

    def drop(self):
        for table in self.schema.tables.values():
            self.execute(table.drop)
        return self

    def add(self, table_name: str, data: dict):
        self.now = str(datetime.datetime.now())
        table: Table = self.schema.tables[table_name]
        max_id = self.get_max_id(table_name)
        columns = ', '.join([c.name for c in table.model.values()])
        values = ','.join([table.get_column_value(c, data, max_id) for c in table.model.values()])
        sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, columns, values)
        self.execute(sql, lastrowid=True)
        record_id = self.results
        return record_id

    def get_max_id(self, table_name):
        records = self.get(table_name)
        id_column = self.schema.tables[table_name].get_id_name()
        max_id = max(records.values(), key=lambda x:x[id_column])[id_column] if records else 0
        return max_id

    def get(self, table_name, query=None):
        table: Table = self.schema.tables[table_name]
        where = ''
        if isinstance(query, dict):
            query_list = []
            for k, v in query.items():
                if isinstance(v, list):
                    query_list_values = []
                    for item in v:
                        sql_list_item_value = (str(item) if isinstance(item, int) else f"'{item}'") if item else ''
                        query_list_values.append(sql_list_item_value)
                    query_list.append(f'{k} in ({",".join(query_list_values)})')
                else:
                    sql_value = (v if isinstance(v, int) else f"'{v}'") if v else ''
                    query_list.append(f'{k} = {sql_value}')
            sql_query = ' and '.join(query_list)
            where = f" WHERE {sql_query}"
        elif isinstance(query, (int, str)):
            id_column = table.get_id_name()
            sql_id_value = (query if isinstance(query, int) else f"'{query}'") if query else ''
            where = f" WHERE {id_column} = {sql_id_value}" if query else ''
        cols = ', '.join([k for k in table.model.keys()])
        self.execute(f"SELECT {cols} from {table_name}{where}", fetch=True)
        records = {}
        for r in self.results:
            record = {}
            for x in range(0, len(table.model.keys())):
                name = list(table.model.keys())[x]
                record[name] = r[x]
            id_field, id_value = table.get_id_field_value(record)
            records[id_value] = record
        return records

    def update(self, table_name: str, data: dict, update: dict):
        self.now = str(datetime.datetime.now())
        table: Table = self.schema.tables[table_name]
        id_column = table.get_id_name()
        id_value = data[id_column] if id_column else None
        record = self.get(table_name, id_value)
        if id_column and record:
            updates = []
            for k, v in update.items():
                column = list(filter(lambda c: c.name == k, table.model.values()))
                if column and k not in ['create_timestamp']:
                    value = v
                    if value is None:
                        value = 'null'
                    elif k == 'last_update_timestamp':
                        value = self.now
                    elif not column[0].type == 'INTEGER':
                        value = f"'{value}'"
                    updates.append(f"{k} = {value}")
            updates_str = ', '.join(updates)
            sql_id_value = (id_value if isinstance(id_value, int) else f"'{id_value}'") if id_value else ''
            self.execute(f"UPDATE {table_name} SET {updates_str} WHERE {id_column} = {sql_id_value}")

    def remove(self, table_name, id_value=None):
        where = ''
        if id_value:
            table = self.schema.tables[table_name]
            id_column = table.get_id_name()
            sql_id_value = (id_value if isinstance(id_value, int) else f"'{id_value}'") if id_value else ''
            where = f' WHERE {id_column} = {sql_id_value}'
        self.execute(f"DELETE FROM {table_name}{where}")

    def execute(self, sql, fetch:bool=False, lastrowid:bool=False):
        self.results = None
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('BEGIN;')
        try:
            cursor.execute(sql)
            if fetch:
                self.results = cursor.fetchall()
            if lastrowid:
                self.results =  cursor.lastrowid
            cursor.execute('COMMIT;')
        except Exception as e:
            print(e)
            cursor.execute('ROLLBACK;')
        self.conn.commit()
        return self

    def connect(self, db_name: str=None):
        if (not hasattr(self, 'conn')):
            self.conn = sqlite3.connect(db_name if db_name else self.schema.db_name)

    def close(self):
        self.conn.close()
        return self

    def remove_db(self):
        try:
            os.remove(self.schema.db_name)
        except:
            pass
        return self
