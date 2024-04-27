from flask import make_response
from flask_restx import Resource, Namespace
from .api_models import project_list, project_input
from app.extensions import db
from datetime import datetime
from flask_jwt_extended import current_user
from app.models import Project, User

authorizations = {
    "jwt": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}
project_ns = Namespace('api/v1', description='Project connected user crud operations')


@project_ns.route("/project")
class ProjectCurd(Resource):
    @project_ns.doc(security="jwt")
    @project_ns.marshal_list_with(project_list)
    def get(self):

        user = User.query.filter_by(id=current_user.id).first()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)
        projects = Project.query.filter_by(owner_id=current_user.id).all()
        return projects

    @project_ns.expect(project_input)
    @project_ns.marshal_with(project_list)
    def post(self):
        check_for_duplicate = Project.query.filter_by(title=project_ns.payload['title']).first()
        if check_for_duplicate:
            return make_response({'message': 'project already exists'}, 409)

        new_project = Project(
            title=project_ns.payload['title'],
            owner_id=current_user.id,
            start_date=datetime.now,
            description=project_ns.payload['description']
        )
        db.session.add(new_project)
        db.session.commit()

        return make_response({'project': new_project}, 201)
