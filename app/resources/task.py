from typing import Union

from flask import make_response
from flask_restx import Resource, Namespace
from app.extensions import db, authorizations
from datetime import datetime
from .api_models import task_create, task_list
from flask_jwt_extended import current_user, jwt_required
from app.models import Task, Project, User, Priority, Status
from app.utils.security_helper import SecurityHelper

task_api = Namespace('api/v1/task', description='Tiiket App Task logic', authorizations=authorizations)


@task_api.route("/")
class MultipleTaskResource(Resource):
    method_decorators = [jwt_required()]

    @task_api.doc(security="jwt")
    @task_api.marshal_list_with(task_create)
    def get(self):
        user = self._get_user()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)
        tasks = self._get_users_tasks()
        return tasks

    @task_api.doc(security="jwt")
    @task_api.expect(task_create)
    @task_api.marshal_with(task_list)
    def post(self):
        new_task = self._create_task()

        db.session.add(new_task)
        db.session.commit()

        return new_task, 201

    def _get_users_tasks(self):
        return Task.query.filter_by(owner_id=current_user.id, is_deleted=False).all()

    def _get_user(self):
        return User.query.filter_by(id=current_user.id).first()

    def _get_project(self, project_id):
        return Project.query.filter_by(owner_id=current_user.id, uid=project_id, is_deleted=False).first_or_404()

    def _check_duplicate(self, title):
        return Task.query.filter_by(title=title, owner_id=current_user.id, is_deleted=False).count()

    def get_priority_enum(self, string_value):
        return next((priority for priority in Priority if priority.value == string_value), Priority.LOW)

    def get_status_enum(self, string_value):
        return next((status for status in Status if status.value == string_value), Status.PENDING)

    def _create_task(self):
        title = task_api.payload.get('title', '')
        priority = self.get_priority_enum(task_api.payload.get('priority', ''))
        status = self.get_status_enum(task_api.payload.get('status', ''))
        due_date = task_api.payload.get('due_date', '')
        description = SecurityHelper.escape_html(task_api.payload.get('description', ''))
        project_id = task_api.payload.get('project_id', '')

        if not title:
            raise ValueError("Title is required")

        if due_date:
            try:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                if due_date < datetime.now().date():
                    raise ValueError("Due date cannot be in the past")
            except ValueError:
                raise ValueError("Invalid due date format. Please provide the date in 'YYYY-MM-DD' format.")

        if not project_id:
            raise ValueError("Project ID is required")

        project = self._get_project(project_id)

        if not project:
            raise ValueError("Project not found")

        # Check if there are tasks with similar titles
        duplicate_count = self._check_duplicate(title)

        # If there are duplicate tasks, append a number to the title
        if duplicate_count:
            title = f"{title} {duplicate_count + 1}"

        return Task(
            title=title,
            owner_id=current_user.id,
            project_id=project.id,
            priority=priority,
            status=status,
            due_date=due_date,
            description=description
        )
