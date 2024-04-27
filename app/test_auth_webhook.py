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

    # cd 
    def test_register_webhook(self):
        # Test registering a new user
        data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        response = self.app.post("/api/auth/webhook/register", json=data)
        self.assertEqual(response.status_code, 201)

    def test_register_existing_user(self):
        # Test registering an existing user
        user = User(username="existinguser", email="existing@example.com")
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        
        data = {
            "username": "existinguser",
            "email": "existing@example.com"
        }
        response = self.app.post("/api/auth/webhook/register", json=data)
        self.assertEqual(response.status_code, 409)

    def test_login_webhook(self):
        # Test logging in with valid credentials
        user = User(username="testuser", email="test@example.com")
        with app.app_context():
            db.session.add(user)
            db.session.commit()

        with patch("app.resources.auth.create_access_token") as mock_create_access_token:
            mock_create_access_token.return_value = "fake_access_token"
            data = {"email": "test@example.com"}
            response = self.app.post("/api/auth/webhook/login", json=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn("access_token", response.json)

    def test_login_invalid_email(self):
        # Test logging in with invalid email
        data = {"email": "invalid_email"}
        response = self.app.post("/api/auth/webhook/login", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Invalid email address")

    def test_login_nonexistent_user(self):
        # Test logging in with nonexistent user
        data = {"email": "nonexistent@example.com"}
        response = self.app.post("/api/auth/webhook/login", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"], "User does not exist")

if __name__ == "__main__":
    unittest.main()
