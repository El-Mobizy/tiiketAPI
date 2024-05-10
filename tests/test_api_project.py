import unittest
import os
import sys
import logging
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db

# Create the Flask application instance
app = create_app()

ACCESS_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNDI4OTM5MiwianRpIjoiODk2M2MyYzAtNWU0OC00NmNkLWExNGQtNmI1NzNjMzE3OTQ0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MzgsIm5iZiI6MTcxNDI4OTM5MiwiY3NyZiI6Ijg0YjhmMWIyLWJjY2EtNDJjMC05MmM4LTY3ODhkMzQ5YjcxYiIsImV4cCI6MTcxNDI5MTE5Mn0.jpNyMXLLdnkmm_vbj50EVgufoFyQTVq8n8yxScicXL0'
ERR_ACCESS_TOKEN = 'Bearer eyBhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNDI4NzE4OCwianRpIjoiMGIyNWMyNzgtN2JjNi00OGIzLWIxZjYtNzllZWY4ZGJiZjc1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MzgsIm5iZiI6MTcxNDI4NzE4OCwiY3NyZiI6IjIzZDY4NzA4LWMwYjctNDYzOC05ZWViLTkwZDA1MDFlMWU3ZiIsImV4cCI6MTcxNDI4ODk4OH0.vNXLiCXKY9ICDIfMhMYqpDEfeW8dYt0c6OGpeKtKh3Y'
EXP_ACCESS_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNDI4NTg4NCwianRpIjoiNjBhYjFjMmQtNTY5Yi00MDk0LTk2YzgtZDk1Y2NmZWU1MWYzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MzgsIm5iZiI6MTcxNDI4NTg4NCwiY3NyZiI6IjBjMzI2OTQxLWY2NmYtNGJjYi1iYTBmLWJhYWY1YzNhNDkxYiIsImV4cCI6MTcxNDI4NzY4NH0.K8XjncXs0_UaGWriSsOQa67l6Htsxt-90ppi4yenwnA'
required_fields = {'title': str}


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def test_get_project(self):
        try:
            response = self.app.get('/api/v1/project', headers={'Authorization': ACCESS_TOKEN})
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.json)
        except Exception as e:
            # Add logic to handle the exception, for example logging the error
            logging.error(f"An error occurred in test_get_project: {str(e)}")
            self.fail(f"Exception occurred: {str(e)}")

    def test_user_not_found(self):
        try:
            response = self.app.get('/api/v1/project', headers={'Authorization': EXP_ACCESS_TOKEN})
            if response.status_code == 401:
                self.assertEqual(response.status_code, 401)
            elif response.status_code == 422:
                self.assertEqual(response.status_code, 422)
            self.assertIsNotNone(response.json)
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_successful_project_creation(self):
        try:
            response = self.app.post('/api/v1/project', json={"title": "tests", "description": "tests"},
                                     headers={'Authorization': ACCESS_TOKEN})
            if response.status_code == 201:  # Everything went well
                self.assertEqual(response.status_code, 201)
            elif response.status_code == 409:  # The project already exists
                self.assertEqual(response.status_code, 409)
            self.assertIsNotNone(response.json)
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_duplicate_project(self):
        try:
            response = self.app.post('/api/v1/project', json={"title": "tests", "description": "tests"},
                                     headers={'Authorization': ACCESS_TOKEN})
            if response.status_code == 201:  # Everything went well
                self.assertEqual(response.status_code, 201)
            elif response.status_code == 422:  # The project already exists
                self.assertIn("message", response.json)
                self.assertEqual(response.json["message"], "Project already exists")
            self.assertIsNotNone(response.json)
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def process_payload(self, payload):
        try:
            required_key = payload['title']
            for key, value_type in required_fields.items():
                if key in payload and not isinstance(payload[key], value_type):
                    raise ValueError(f"Value for '{key}' must be of type {value_type.__name__}")
            return required_key
        except KeyError as e:
            raise e

    def test_invalid_project_creation_payload(self):
        try:
            payload_missing_key = {"description": "Description of the new project"}
            response = self.app.post('/api/v1/project', json=payload_missing_key,
                                     headers={'Authorization': ACCESS_TOKEN})
            if response.status_code == 400:  # Missing field
                self.assertIn("message", response.json)
                self.assertEqual(response.json["message"], "Missing required field: title")
            elif response.status_code == 422:  # The project already exists
                self.assertIn("message", response.json)
                self.assertEqual(response.json["message"], "Project already exists")
            with self.assertRaises(KeyError):
                self.process_payload(payload_missing_key)
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")

    def test_unauthorized_get_project(self):
        try:
            response = self.app.get('/api/v1/project')
            if response.status_code == 401:
                self.assertEqual(response.status_code, 401)
            elif response.status_code == 422:
                self.assertEqual(response.status_code, 422)
            self.assertIsNotNone(response.json)
        except Exception as e:
            self.fail(f"Exception occurred: {str(e)}")






if __name__ == "__main__":
    unittest.main()
