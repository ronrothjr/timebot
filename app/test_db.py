import unittest, os
from db import Sqlite3DB, DatabaseSchema
from utils import Utils


class TestDB(unittest.TestCase):

    def tearDown(self) -> None:
        self.remove_db()

    def remove_db(self) -> None:
        try:
            os.remove('app.db')
        except:
            pass

    def test_can_instanciate_db(self):
        self.db = Sqlite3DB(DatabaseSchema(db_name='app.db', tables={
            'test': {
                'test': {
                    'name': 'test',
                    'type': 'TEXT'
                }
            },
            'test2': {
                'testid': {
                    'name': 'testid',
                    'type': 'INTEGER',
                    'ref': 'test(testid)',
                    'trigger': 'CASCADE'
                }
            }
        }))
        self.assertIsInstance(self.db, Sqlite3DB)
        self.assertIsInstance(self.db.schema.db_name, str)
        self.assertIsInstance(self.db.schema.tables, dict)
        self.assertTrue(callable(self.db.add))
        self.assertTrue(callable(self.db.get))
        self.assertTrue(callable(self.db.execute))

    def test_can_add_read_update_and_remove_record(self):
        self.db = Sqlite3DB(DatabaseSchema(db_name='app.db', tables={
            'test': {
                'test': {
                    'name': 'test',
                    'type': 'TEXT'
                }
            },
            'test2': {
                'testid': {
                    'name': 'testid',
                    'type': 'INTEGER',
                    'ref': 'test(testid)',
                    'trigger': 'CASCADE'
                }
            }
        }))
        self.db.add('test', {'test': 'tested'})
        record = self.db.get('test')[1]
        self.assertEqual(record['test'], 'tested')
        self.db.add('test2', {'testid': 1})
        child = self.db.get('test2')[1]
        self.assertEqual(child['testid'], 1)
        self.db.update('test', record, {'test': 'tested2'})
        record = self.db.get('test')[1]
        self.assertEqual(record['test'], 'tested2')
        self.db.remove('test', record['testid'])
        records = self.db.get('test')
        self.assertTrue(len(records) == 0)
        child = self.db.get('test2')
        self.assertTrue(len(child) == 0)

    def test_can_add_read_update_and_remove_record_with_text_primary_key(self):
        self.db = Sqlite3DB(DatabaseSchema(db_name='app.db', tables={
            'test': {
                'test': {
                    'name': 'test',
                    'type': 'TEXT',
                    'id': True
                }
            },
            'test2': {
                'test': {
                    'name': 'test',
                    'type': 'TEXT',
                    'ref': 'test(test)',
                    'trigger': 'CASCADE'
                },
                'test2': {
                    'name': 'test2',
                    'type': 'TEXT',
                    'id': True
                }
            }
        }))
        self.db.add('test', {'test': 'tested'})
        record = self.db.get('test', 'tested')['tested']
        self.assertEqual(record['test'], 'tested')
        self.db.add('test2', {'test': 'tested', 'test2': 'tested2'})
        child = self.db.get('test2')['tested2']
        self.assertEqual(child['test'], 'tested')
        self.assertEqual(child['test2'], 'tested2')
        self.db.update('test', record, {'test': 'tested2'})
        record = self.db.get('test')['tested2']
        self.assertEqual(record['test'], 'tested2')
        child = self.db.get('test2')['tested2']
        self.assertEqual(child['test'], 'tested2')
        self.db.remove('test', record['test'])
        records = self.db.get('test')
        self.assertTrue(len(records) == 0)
        child = self.db.get('test2')
        self.assertTrue(len(child) == 0)

    def test_can_handle_timecard_data(self):
        self.db = Sqlite3DB(DatabaseSchema(**Utils.get_schema()))
        self.db.add('project', {'code': 'DRG-403009'})
        self.db.add('project', {'code': 'DRG-403001'})
        self.db.add('project', {'code': 'DRG-403005'})
        self.db.add('project', {'code': 'DRG-413005'})
        self.db.add('timecard', {'begin_date': '2022-02-20', 'end_date': '2022-02-26'})
        day = {'begin_date': '2022-02-20', 'weekday': 'Monday'}
        day['dayid'] = self.db.add('day', day)
        entry = {'dayid': day['dayid'], 'begin': '0900', 'end': '1600', 'code': 'DRG-403009'}
        entry['entryid'] = self.db.add('entry', entry)
        self.db.update('entry', entry, {'begin': '0830'})
        entries = self.db.get('entry')
        self.assertEqual(len(entries), 1, 'entries should have only 1')
        entry = entries[entry['entryid']]
        self.assertEqual(entry['end'], '1600', '0830 entry should end at 4pm')
        self.db.update('day', day, {'weekday': 'Tuesday'})


if __name__ == '__main__':
    unittest.main()