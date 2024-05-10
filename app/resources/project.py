from typing import Union

from flask import make_response
from flask_restx import Resource, Namespace
from .api_models import project_list, project_input
from app.extensions import db, authorizations
from datetime import datetime
from flask_jwt_extended import current_user, jwt_required
from app.models import Project, User

project_api = Namespace('api/v1', description='Tiiket App bussines logic', authorizations=authorizations)


@project_api.route("/project")
class ProjectResource(Resource):
    method_decorators = [jwt_required()]

    @project_api.doc(security="jwt")
    @project_api.marshal_list_with(project_list)
    def get(self):

        user = User.query.filter_by(id=current_user.id).first()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)
        projects = Project.query.filter_by(owner_id=current_user.id, is_deleted=False).all()
        return projects

    @project_api.doc(security="jwt")
    @project_api.expect(project_input)
    @project_api.marshal_with(project_list)
    def post(self):
        try:
            title = project_api.payload['title']
        except KeyError:
            return make_response({'message': 'Missing required field: title'}, 400)

        check_for_duplicate = Project.query.filter_by(title=title).first()
        if check_for_duplicate:
            return make_response({'message': 'Project already exists'}, 422)

        new_project = Project(
            title=title,
            owner_id=current_user.id,
            start_date=datetime.now(),
            description=project_api.payload['description']
        )

        db.session.add(new_project)
        db.session.commit()

        return (new_project, 201)


@project_api.route("/project/<project_uid>")
class SingleProjectResource(Resource):
    method_decorators = [jwt_required()]

    @project_api.doc(security="jwt")
    @project_api.marshal_with(project_list)
    def get(self, project_uid=Union[str, None]):
        try:
            project = Project.query.filter_by(owner_id=current_user.id, uid=project_uid, is_deleted=True).first_or_404()
            project.description = project_api.payload['description']
            db.session.commit()
            return project, 201

        except Exception as e:
            return str(e), 500

    @project_api.doc(security="jwt")
    @project_api.expect(project_input)
    @project_api.marshal_with(project_list)
    def put(self, project_uid=Union[str, None]):
        try:
            payload = project_api.payload
            title = payload.get('title')
            if not title:
                return make_response({'message': 'Missing required field: title'}, 400)

            project = Project.query.filter_by(owner_id=current_user.id, uid=project_uid, is_deleted=True).first()
            if not project:
                return make_response({'message': 'Project not found'}, 404)

            project.title = str(title)  # Ensure title is converted to a string
            project.description = payload.get('description', '')
            db.session.commit()
            return project, 201

        except Exception as e:
            return make_response({'message': f'Exception occurred: {str(e)}'}, 500)


    @project_api.doc(security="jwt")
    @project_api.expect(project_input)
    @project_api.marshal_with(project_list)
    def delete(self, project_uid=Union[str, None]):
        try:
            project = Project.query.filter_by(owner_id=current_user.id, uid=project_uid, is_deleted=True).first_or_404()
            db.session.delete(project)
            db.session.commit()
            return project

        except Exception as e:
            return str(e), 500
