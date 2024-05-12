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


task_create = api.model('TaskCreate', {
    'title': fields.String,
    'due_date': fields.DateTime,
    'project_id': fields.String,
})

task_list = api.model('TaskList', {
    'title': fields.String,
    'due_date': fields.Date,
    'project_id': fields.String,
    'status': fields.String,
    'priority': fields.String,
    'assignee_id': fields.String,
    'description': fields.String,
})

user_model = api.model("UserModel", {
    "uid": fields.String,
    "username": fields.String,
})
login_model = api.model("LoginModel", {
    "email": fields.String,
    "username": fields.String,
})

