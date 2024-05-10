import unittest
import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User

# Create the Flask application instance
app = create_app()


class AuthWebhookTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
        self.app = app.test_client()
        with app.app_context():
            db.create_all()


    def test_login_with_existing_user(self):
        # Test logging in with valid credentials
        # Mock the create_access_token function
        with app.app_context():
            with patch("app.resources.auth.create_access_token") as mock_create_access_token:
                mock_create_access_token.return_value = "fake_access_token"
                try:
                    user = User.query.filter_by(email="tests@example.com", username="testuser").first()
                    if not user:
                        user = User(username="testuser", email="tests@example.com")
                        db.session.add(user)
                        db.session.commit()

                    data = {"email": "tests@example.com"}
                    response = self.app.post("/api/auth/webhook/login", json=data)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn("access_token", response.json)
                except Exception as e:
                    self.fail(f"Exception occurred: {str(e)}")

    def test_login_with_invalid_credentials(self):
        # Test logging in with invalid credentials
        data = {"email": "test_@example.com"}
        try:
            response = self.app.post("/api/auth/webhook/login", json=data)
            self.assertEqual(response.status_code, 401)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Invalid email address or password")
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_login_with_no_credentials(self):
        # Test logging in with no credentials
        data = {}
        try:
            response = self.app.post("/api/auth/webhook/login", json=data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Invalid email address or password")
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_login_with_inactive_user(self):
        # Test logging in with an inactive user
        with app.app_context():
            data = {"email": "test_inactive@example.com", "username": "test_inactive@example.com", "is_active": False}
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                new_user = User(**data)
                db.session.add(new_user)
                db.session.commit()

            try:
                response = self.app.post("/api/auth/webhook/login", json=data)
                self.assertEqual(response.status_code, 401)
                self.assertIn("error", response.json)
                self.assertEqual(response.json["error"], "User is inactive")
            except Exception as e:
                self.fail(f"Exception occurred: {str(e)}")

    def test_login_with_non_existing_user(self):
        # Test logging in with invalid credentials (email) and a non-existing user in the database
        data = {"email": "nonexistent@example.com"}
        try:
            response = self.app.post("/api/auth/webhook/login", json=data)
            self.assertEqual(response.status_code, 401)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Invalid email address or password")
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_successful_registration(self):
        # Test registering a new user with valid credentials and no existing user with the same email or username
        data = {"username": "testusernew", "email": "testnew@example.com"}
        try:
            response = self.app.post("/api/auth/webhook/register", json=data)
            if response.status_code == 201:
                self.assertIn("message", response.json)
                self.assertEqual(response.json["message"], "User created successfully")
            elif response.status_code == 409:
                self.assertIn("error", response.json)
                self.assertEqual(response.json["error"], "User already exists")
            else:
                self.fail(f"Unexpected response status code: {response.status_code}")
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_registration_with_existing_email(self):
        with app.app_context():
            # Test registering a new user with an email that already exists in the database

            data = {"username": "testuser2", "email": "tests@example.com"}
            try:
                response = self.app.post("/api/auth/webhook/register", json=data)
                self.assertEqual(response.status_code, 409)
                self.assertIn("error", response.json)
                self.assertEqual(response.json["error"], "User already exists")
            except Exception as e:
                self.fail(f"Exception occurred: {str(e)}")

    def test_registration_with_existing_username(self):
        with app.app_context():
            # Test registering a new user with a username that already exists in the database

            data = {"username": "testuser", "email": "test2@example.com"}
            try:
                response = self.app.post("/api/auth/webhook/register", json=data)
                self.assertEqual(response.status_code, 409)
                self.assertIn("error", response.json)
                self.assertEqual(response.json["error"], "User already exists")
            except Exception as e:
                self.fail(f"Exception occurred: {str(e)}")


if __name__ == "__main__":
    unittest.main()
