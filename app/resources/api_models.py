from flask_restx import fields
from app.extensions import api

project_list = api.model('ProjectList', {
    'uid': fields.String,
    'title': fields.String,
    'description': fields.String
})

project_input = api.model('ProjectInput', {
    'title': fields.String,
    'description': fields.String
})

user_model = api.model("UserModel", {
    "uid": fields.String,
    "username": fields.String,
})
login_model = api.model("LoginModel", {
    "email": fields.String,
    "username": fields.String,
})

