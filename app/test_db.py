import unittest
from db import DB


class TestDB(unittest.TestCase):
    
    def setUp(self):
        self.db = DB(db_name='test.db', tables={
            'test': [{
                'name': 'test',
                'type': 'text',
                'id': True
            }]
        })

    def tearDown(self) -> None:
        self.db.remove('test', 1)

    def test_can_instanciate_db(self):
        self.assertIsInstance(self.db, DB)
        self.assertIsInstance(self.db.db_name, str)
        self.assertIsInstance(self.db.tables, dict)
        self.assertTrue(callable(self.db.create))
        self.assertTrue(callable(self.db.add))
        self.assertTrue(callable(self.db.get))
        self.assertTrue(callable(self.db.execute))

    def test_can_add_and_read_record(self):
        self.db.add('test', {'test': 'tested'})
        records = self.db.get('test')
        self.assertEqual(records[0]['test'], 'tested')

if __name__ == '__main__':
    unittest.main()