import re
import secrets
from flask import request, make_response
from ..models import User
from .. import app
import jwt
from functools import wraps

class SecurityHelper:
    @staticmethod
    def sanitize_input(input_string):
        return re.sub(r'[;\'"]', '', input_string)

    @staticmethod
    def escape_html(input_string):
        return input_string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    @staticmethod
    def generate_csrf_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_csrf_token(request_token, session_token):
        return request_token == session_token


    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            elif 'Authorization' in request.headers:
                token = request.headers['Authorization']
            elif not token:
                return make_response({'message': 'Token is missing!'}, 401)

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.filter_by(uid=data['user_id']).first()
            except Exception as e:
                print(e)
                return make_response({'message': 'Token is invalid!'}), 401
            return f(current_user, *args, **kwargs)

        return decorated