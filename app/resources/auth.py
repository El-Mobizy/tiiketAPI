from flask import make_response, jsonify
from flask_restx import Resource, Namespace
from app.extensions import db
from datetime import datetime
from flask_jwt_extended import create_access_token
from app.models import User
from app.resources.api_models import login_model, user_model
from app.utils.security_helper import SecurityHelper


authentication_webhook_ns = Namespace('api/auth', description='Authentication Web hook')


@authentication_webhook_ns.route("/webhook/login")
class LoginWebhook(Resource):
    @authentication_webhook_ns.expect(login_model)
    def post(self):
        email = SecurityHelper.sanitize_input(authentication_webhook_ns.payload["email"])
        
        if not SecurityHelper.validate_email(email):
            return make_response({"error": "Invalid email address"}, 400)
        
        user = User.query.filter_by(email=email).first()
        if user is None:
            return make_response({"error": "User does not exist"}, 401)
        
        user.last_login = datetime.now()
        db.session.commit()
        
        user_data = {
            "id": user.uid,
            "username": user.username,
            "email": user.email,
        }

        response_data = {
            "message": "Logged in",
            "access_token": create_access_token(identity=user_data,expires_delta=datetime.timedelta(minutes=30))
        }

        return response_data, 200


@authentication_webhook_ns.route("/webhook/register")
class RegisterWebhook(Resource):
    @authentication_webhook_ns.expect(login_model)
    def post(self):

        username = SecurityHelper.sanitize_input(authentication_webhook_ns.payload["username"])
        email = SecurityHelper.sanitize_input(authentication_webhook_ns.payload["email"])

        if not SecurityHelper.validate_email(email):
            return make_response({"error": "Invalid email address"}, 400)
        if User.query.filter_by(email=email).first() is not None:
            return make_response({"error": "Email already exists"}, 409)

        if not username:
            username = email
        if User.query.filter_by(username=username).first() is not None:
            return make_response({"error": "Username already exists"}, 409)
        

        user = User(username=username, is_active=True, email=email)

        db.session.add(user)
        db.session.commit()
        return make_response({'message': 'User created successfully'}, 201)
