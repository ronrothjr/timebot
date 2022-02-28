import unittest
from repository import Repository
from db import DB, DatabaseSchema
from utils import Utils


class TestRepository(unittest.TestCase):

    def setUp(self) -> None:
        self.repository = Repository(DB, DatabaseSchema(**Utils.get_schema()))

    def test_can_instantiate_a_repository(self):
        self.assertIsInstance(self.repository, Repository)
        self.assertIsInstance(self.repository.db, DB)

