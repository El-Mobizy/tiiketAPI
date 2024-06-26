from flask import Flask
import os
from dotenv import load_dotenv
from app.extensions import api, db, jwt
from app.api_setup import setup_namespaces
from app.models import User

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
    app.config["JWT_SECRET_KEY"] = os.getenv('SECRET')

    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    setup_namespaces(api)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).first()

    return app


# Create the Flask application instance
app = create_app()
