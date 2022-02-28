import unittest, os
from db import DB


class TestDB(unittest.TestCase):

    def tearDown(self) -> None:
        self.remove_db()

    def remove_db(self) -> None:
        try:
            os.remove('test.db')
        except:
            pass

    def test_can_instanciate_db(self):
        self.db = DB(db_name='test.db', tables={
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
        })
        self.assertIsInstance(self.db, DB)
        self.assertIsInstance(self.db.db_name, str)
        self.assertIsInstance(self.db.tables, dict)
        self.assertTrue(callable(self.db.create))
        self.assertTrue(callable(self.db.add))
        self.assertTrue(callable(self.db.get))
        self.assertTrue(callable(self.db.execute))

    def test_can_add_read_update_and_remove_record(self):
        self.db = DB(db_name='test.db', tables={
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
        })
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
        self.db = DB(db_name='test.db', tables={
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
        })
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
        timebot_tables = {}
        timebot_tables['timecard'] = {
            'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'id': True},
            'end_date': {'name': 'end_date', 'type': 'TEXT'}
        }
        timebot_tables['day'] = {
            'begin_date': {'name': 'begin_date', 'type': 'TEXT', 'ref': 'timecard(begin_date)', 'trigger': 'CASCADE'},
            'weekday': {'name': 'weekday', 'type': 'TEXT', 'id': True}
        }
        timebot_tables['project'] = {
            'code': {'name': 'code', 'type': 'TEXT', 'id': True}
        }
        timebot_tables['entry'] = {
            'weekday': {'name': 'weekday', 'type': 'TEXT', 'ref': 'day(weekday)', 'trigger': 'CASCADE'},
            'begin': {'name': 'begin', 'type': 'TEXT', 'id': True},
            'end': {'name': 'end', 'type': 'TEXT'},
            'code': {'name': 'code', 'type': 'TEXT', 'ref': 'project(code)', 'trigger': 'CASCADE'}
        }
        self.db = DB(db_name='test.db', tables=timebot_tables)
        self.db.add('project', {'code': 'DRG-403009'})
        self.db.add('project', {'code': 'DRG-403001'})
        self.db.add('project', {'code': 'DRG-403005'})
        self.db.add('project', {'code': 'DRG-413005'})
        self.db.add('timecard', {'begin_date': '20220220', 'end_date': '20220226'})
        day = {'begin_date': '20220220', 'weekday': 'Monday'}
        self.db.add('day', day)
        entry = {'weekday': 'Monday', 'begin': '0900', 'end': '1600', 'code': 'DRG-403009'}
        self.db.add('entry', entry)
        self.db.update('entry', entry, {'begin': '0830'})
        entries = self.db.get('entry')
        self.assertEqual(len(entries), 1, 'entries should have only 1')
        entry = entries['0830']
        self.assertEqual(entry['end'], '1600', '0830 entry should end at 4pm')
        self.db.update('day', day, {'weekday': 'Tuesday'})
        entry = self.db.get('entry')['0830']
        self.assertEqual(entry['weekday'], 'Tuesday', '0830 should be moved to Tuesday')


if __name__ == '__main__':
    unittest.main()