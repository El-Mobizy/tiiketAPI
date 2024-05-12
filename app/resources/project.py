from typing import Union

from flask import make_response
from flask_restx import Resource, Namespace
from .api_models import project_list, project_input
from app.extensions import db, authorizations
from datetime import datetime
from flask_jwt_extended import current_user, jwt_required
from app.models import Project, User
from app.utils.security_helper import SecurityHelper

project_api = Namespace('api/v1/project', description='Tiiket App bussines logic', authorizations=authorizations)


@project_api.route("/")
class ProjectResource(Resource):
    method_decorators = [jwt_required()]

    @project_api.doc(security="jwt")
    @project_api.marshal_list_with(project_list)
    def get(self):

        user = self._get_user()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)
        projects = self._get_users_projects()
        return projects

    @project_api.doc(security="jwt")
    @project_api.expect(project_input)
    @project_api.marshal_with(project_list)
    def post(self):
        title = self._check_for_title()
        if not title:
            return make_response({'message': 'Missing required field: title'}, 400)

        if self._is_duplicate(title):
            return make_response({'message': 'Project already exists'}, 422)

        new_project = self._create_project(title)

        db.session.add(new_project)
        db.session.commit()

        return new_project, 201

    @project_api.doc(security="jwt")
    def delete(self):
        try:
            user = self._get_user()
            if user is None:
                return make_response({'message': 'No such user found'}, 404)

            project_ids = project_api.payload['project_ids']
            if not project_ids:
                return make_response({'message': 'Missing required field: project_ids'}, 400)

            for project_id in project_ids:
                project = self._get_project(project_id)
                project.is_deleted = True
                db.session.commit()
                return make_response({'message': 'Project deleted successfully'}, 200)

        except Exception as e:
            return str(e), 500

    def _check_for_title(self):
        try:
            title = project_api.payload['title']
            if not title:
                return make_response({'message': 'Missing required field: title'}, 400)
            return title
        except KeyError:
            return make_response({'message': 'Missing required field: title'}, 400)

    def _get_user(self):
        return User.query.filter_by(id=current_user.id).first()

    def _get_users_projects(self):
        return Project.query.filter_by(owner_id=current_user.id, is_deleted=False).all()

    def _is_duplicate(self, title):
        return Project.query.filter_by(title=title, owner_id=current_user.id, is_deleted=False).first() is not None

    def _get_project(self, project_id):
        return Project.query.filter_by(owner_id=current_user.id, uid=project_id, is_deleted=False).first_or_404()

    def _create_project(self, title):
        description = SecurityHelper.escape_html(project_api.payload.get('description', ''))
        return Project(
            title=SecurityHelper.escape_html(title),
            owner_id=current_user.id,
            start_date=datetime.now(),
            description=description
        )


@project_api.route("/<project_uid>")
class SingleProjectResource(Resource):
    method_decorators = [jwt_required()]

    @project_api.doc(security="jwt")
    @project_api.expect(project_list)
    @project_api.marshal_with(project_list)
    def get(self, project_uid=Union[str, None]):
        user = User.query.filter_by(id=current_user.id).first()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)

        try:
            project = self._get_project(project_uid)
            return project, 200

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

            project = self._get_project(project_uid)
            if not project:
                return make_response({'message': 'Project not found'}, 404)

            self._update_project(project, payload)
            return project, 201

        except Exception as e:
            return make_response({'message': f'Exception occurred: {str(e)}'}, 500)

    @project_api.doc(security="jwt")
    def delete(self, project_uid=Union[str, None]):
        try:
            project = Project.query.filter_by(owner_id=current_user.id, uid=project_uid).first_or_404()
            project.is_deleted = True
            db.session.commit()
            return make_response({'message': 'Project deleted successfully'}, 200)

        except Exception as e:
            return str(e), 500

    def _get_project(self, project_uid):
        return Project.query.filter_by(owner_id=current_user.id, uid=project_uid, is_deleted=False).first()

    def _update_project(self, project, payload):
        project.title = str(SecurityHelper.escape_html(payload.get('title')))
        project.description = SecurityHelper.escape_html(payload.get('description', ''))
        db.session.commit()
