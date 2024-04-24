from functools import wraps
from . import app
from flask import request, make_response, jsonify, session
from .models import User, UserToken, db
import jwt
from datetime import datetime, timedelta
from .utils.security_helper import SecurityHelper


@app.post('/api/hook_user_signup')
def create_user():
    data = request.get_json()
    # return jsonify({"secret": app.config['SECRET_KEY']}), 200
    check_user = User.query.filter_by(email=data.get('email')).first()
    if check_user:
        return make_response({'message': "user already exists"}, 409)

    user = User(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password')
    )

    db.session.add(user)
    db.session.commit()

    return make_response({'message': "user created"}, 201)


@app.post('/api/hook_user_signin')
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user:
        return make_response({'message': 'User not found'}, 401)

    token = jwt.encode(
        {
            'user_id': user.uid,
            'exp': datetime.now() + timedelta(minutes=30),
        },
        app.config['SECRET_KEY'],
        algorithm='HS256')

    user_token = UserToken.query.filter_by(user_id=user.id).first()
    if not user_token:
        user_token = UserToken(token=token, user_id=user.id)
        db.session.add(user_token)
    else:
        user_token.token = token

    db.session.commit()

    csrf_token = SecurityHelper.generate_csrf_token()
    session['csrf_token'] = csrf_token

    response = make_response(jsonify(
        {'message': 'User authenticated',
         'user_token': user_token.token
         }), 200)
    response.headers['X-CSRF-Token'] = csrf_token
    return response


@app.route('/api/logout')
def logout():
    # Clear the session
    session.clear()
    return make_response({'message': 'User logged out'}, 200)


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
        except:
            return make_response({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated
