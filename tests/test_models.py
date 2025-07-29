"""
Test cases for Account Model
"""

import logging
import unittest
import os
from service import create_app
from service.models import Account, DataValidationError, db
from tests.factories import AccountFactory

# Set the database URI for testing
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  Account   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(unittest.TestCase):
    """Test Cases for Account Model"""

    @classmethod
    def setUpClass(cls):
        """Runs once before the entire test suite"""
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["DEBUG"] = False
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        cls.app.logger.setLevel(logging.CRITICAL)

        Account.init_db(cls.app)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        """Runs once after the entire test suite"""
        pass  # Optional cleanup

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_account(self):
        """It should Create an Account and assert that it exists"""
        fake_account = AccountFactory()
        account = Account(
            name=fake_account.name,
            email=fake_account.email,
            address=fake_account.address,
            phone_number=fake_account.phone_number,
            date_joined=fake_account.date_joined,
        )
        self.assertIsNotNone(account)
        self.assertIsNone(account.id)
        self.assertEqual(account.name, fake_account.name)
        self.assertEqual(account.email, fake_account.email)

    def test_add_a_account(self):
        """It should Create an account and add it to the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        account.create()
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

    def test_read_account(self):
        """It should Read an account"""
        account = AccountFactory()
        account.create()
        found = Account.find(account.id)
        self.assertEqual(found.id, account.id)

    def test_update_account(self):
        """It should Update an account"""
        account = AccountFactory(email="old@email.com")
        account.create()
        self.assertEqual(account.email, "old@email.com")
        account.email = "new@email.com"
        account.update()
        updated = Account.find(account.id)
        self.assertEqual(updated.email, "new@email.com")

    def test_delete_an_account(self):
        """It should Delete an account from the database"""
        account = AccountFactory()
        account.create()
        self.assertIsNotNone(account.id)
        account.delete()
        accounts = Account.all()
        self.assertEqual(len(accounts), 0)

    def test_list_all_accounts(self):
        """It should List all Accounts in the database"""
        self.assertEqual(Account.all(), [])
        for account in AccountFactory.create_batch(5):
            account.create()
        accounts = Account.all()
        self.assertEqual(len(accounts), 5)

    def test_find_by_name(self):
        """It should Find an Account by name"""
        account = AccountFactory()
        account.create()
        found = Account.find_by_name(account.name)
        self.assertGreater(len(found), 0)
        self.assertEqual(found[0].name, account.name)

    def test_serialize_an_account(self):
        """It should Serialize an account"""
        account = AccountFactory()
        account.create()
        serial = account.serialize()
        self.assertEqual(serial["id"], account.id)
        self.assertEqual(serial["name"], account.name)

    def test_deserialize_an_account(self):
        """It should Deserialize an account"""
        account = AccountFactory()
        account.create()
        data = account.serialize()
        new_account = Account()
        new_account.deserialize(data)
        self.assertEqual(new_account.name, account.name)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an account with a KeyError"""
        account = Account()
        with self.assertRaises(DataValidationError):
            account.deserialize({})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an account with a TypeError"""
        account = Account()
        with self.assertRaises(DataValidationError):
            account.deserialize([])
