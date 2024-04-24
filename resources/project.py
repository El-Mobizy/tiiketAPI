from flask import request, make_response, jsonify, Blueprint, session
from ..models import Project, User, db
from ..utils.security_helper import SecurityHelper
from datetime import datetime

project_bp = Blueprint('project', __name__)


@project_bp.get('/api/project/user_projects')
def get_user_projects():
    csrf_token = request.headers.get('X-CSRF-Token')
    session_token = session.get('csrf_token')
    if not SecurityHelper.validate_csrf_token(csrf_token, session_token):
        return make_response({'message': 'Invalid CSRF token'}, 403)

    try:
        data = request.get_json()
        if not all([data['userId']]):
            return jsonify({"error": "Missing userId in the payload"}), 400

        user = User.query.filter_by(uid=data['userId']).first()
        if user is None:
            return make_response({'message': 'No such user found'}, 404)

        projects = Project.query.filter_by(owner_id=user.id).all()
        response = [project.serialize() for project in projects]

        session['csrf_token'] = SecurityHelper.generate_csrf_token()
        response = make_response(jsonify({'user_projects': response}), 200)
        response.headers['X-CSRF-Token'] = csrf_token
        return response
    except Exception as e:
        return make_response({'error': 'An error occurred when fetching your projects.'}, 500)


@project_bp.post('/api/project/create_project')
@SecurityHelper.token_required
def create_project(current_user):
    csrf_token = request.headers.get('X-CSRF-Token')
    session_token = session.get('csrf_token')
    if not SecurityHelper.validate_csrf_token(csrf_token, session_token):
        return make_response({'message': 'Invalid CSRF token'}, 403)

    data = request.get_json()
    check_for_duplicate = Project.query.filter_by(title=data.get('title')).first()
    print(data)
    if not all(['title' in data]):
        return make_response({'message': 'title and owner_id are required'}, 400)
    if check_for_duplicate:
        return make_response({'message': 'project already exists'}, 409)

    new_project = Project(
        title=data.get('title'),
        owner_id=current_user.id,
        start_date=datetime.now,
        description=data.get('description')
    )
    db.session.add(new_project)
    db.session.commit()

    return jsonify({'project': new_project.serialize()}), 200


@project_bp.put('/api/project/<uuid:project_uid>')
def update_project(project_uid):
    project = Project.query.filter_by(uid=str(project_uid)).first_or_404()
    if not project:
        return make_response({'message': 'project not found'}, 404)

    to_update = request.get_json()
    if not all(['title' in to_update, 'owner_id' in to_update]):
        return make_response({'message': 'title and owner_id are required'}, 400)
    for key in to_update:
        setattr(project, key, to_update[key])
    db.session.commit()
    return jsonify({'project': project.serialize()}), 200
