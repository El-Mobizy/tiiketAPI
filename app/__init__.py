from flask import Flask
import os
from dotenv import load_dotenv
from app.extensions import api, db, jwt
from app.resources.project import project_ns
from app.resources.auth import authentication_webhook_ns

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
    app.config["JWT_SECRET_KEY"] = os.getenv('SECRET')

    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    api.add_namespace(project_ns)
    api.add_namespace(authentication_webhook_ns)

    return app

# Create the Flask application instance
app = create_app()
