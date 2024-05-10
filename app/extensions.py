from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager

api = Api()
db = SQLAlchemy()
jwt = JWTManager()

authorizations = {
    "jwt": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}
