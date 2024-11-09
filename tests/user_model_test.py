import unittest
from mongoengine import connect, disconnect
from datetime import datetime
import bcrypt
import re

# Import your User model
from db_models import User

class TestUserModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Connect to the local MongoDB instance with the GOAL_TRACKER database
        connect('GOAL_TRACKER', host='mongodb://localhost:27017/GOAL_TRACKER')

    @classmethod
    def tearDownClass(cls):
        # Disconnect from the local MongoDB instance
        disconnect()

    def setUp(self):
        
        # Clear the users collection before each test
        User.objects.delete()

    def test_create_user(self):
        user = User(username="john_doe", email="john@example.com")
        user.set_password("securepassword123")
        user.validate_email()
        user.save()

        # Check if the user was saved correctly
        saved_user = User.objects.get(username="john_doe")
        self.assertEqual(saved_user.email, "john@example.com")
        self.assertTrue(bcrypt.checkpw("securepassword123".encode('utf-8'), saved_user.password.encode('utf-8')))
        self.assertIsInstance(saved_user.created_at, datetime)
        self.assertIsInstance(saved_user.updated_at, datetime)

    def test_update_user(self):
        user = User(username="sham", email="sham@example.com")
        user.set_password("password123")
        user.validate_email()
        user.save()

        # Update the user
        user.email = "shamvaidya@example.com"
        user.save()

        # Check if the user was updated correctly
        updated_user = User.objects.get(username="sham")
        self.assertEqual(updated_user.email, "shamvaidya@example.com")
        self.assertTrue(bcrypt.checkpw("password123".encode('utf-8'), updated_user.password.encode('utf-8')))
        self.assertIsInstance(updated_user.created_at, datetime)
        self.assertIsInstance(updated_user.updated_at, datetime)

    def test_invalid_email(self):
        user = User(username="john_doe", email="invalid_email")
        user.set_password("securepassword123")

        # Check if an invalid email raises a ValueError
        with self.assertRaises(ValueError):
            user.validate_email()

    def test_password_hashing(self):
        user = User(username="john_doe", email="john@example.com")
        user.set_password("securepassword123")

        # Check if the password is hashed correctly
        self.assertTrue(bcrypt.checkpw("securepassword123".encode('utf-8'), user.password.encode('utf-8')))

    def test_unique_username(self):
        user1 = User(username="john_doe", email="john@example.com")
        user1.set_password("securepassword123")
        user1.validate_email()
        user1.save()

        # Attempt to create another user with the same username
        user2 = User(username="john_doe", email="john.doe@example.com")
        user2.set_password("anotherpassword")
        user2.validate_email()

        # Check if a NotUniqueError is raised
        with self.assertRaises(Exception):  # MongoEngine raises a NotUniqueError
            user2.save()

if __name__ == '__main__':
    unittest.main()