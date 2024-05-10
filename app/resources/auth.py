from flask import make_response, jsonify
from flask_restx import Resource, Namespace
from app.extensions import db
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app.models import User
from app.resources.api_models import login_model, user_model
from app.utils.security_helper import SecurityHelper

authentication_webhook_ns = Namespace('api/auth', description='Authentication Web hook')


@authentication_webhook_ns.route("/webhook/login")
class LoginWebhook(Resource):
    @authentication_webhook_ns.expect(login_model)
    def post(self):
        try:
            email = authentication_webhook_ns.payload.get("email")
            if not email or not SecurityHelper.validate_email(email):
                return make_response({"error": "Invalid email address or password"}, 400)

            user = User.query.filter_by(email=email).first()
            if not user:
                return make_response({"error": "Invalid email address or password"}, 401)

            if user.is_active is False:
                return make_response({"error": "User is inactive"}, 401)

            user.last_login = datetime.now()
            db.session.commit()

            user_data = {
                "id": user.uid,
                "username": user.username,
                "email": user.email,
            }

            access_token = create_access_token(identity=user, expires_delta=timedelta(minutes=30))
            response_data = {"message": "Logged in", "access_token": access_token}

            return response_data, 200
        except Exception as e:
            return make_response({"error": str(e)}, 500)


@authentication_webhook_ns.route("/webhook/register")
class RegisterWebhook(Resource):
    @authentication_webhook_ns.expect(login_model)
    def post(self):
        try:
            payload = authentication_webhook_ns.payload
            username = payload.get("username")
            email = payload.get("email")

            if not email or not SecurityHelper.validate_email(email):
                return make_response({"error": "Invalid email address"}, 400)

            if User.query.filter_by(email=email, is_active=True).first():
                return make_response({"error": "User already exists"}, 409)

            username = username or email
            if User.query.filter_by(username=username, is_active=True).first():
                return make_response({"error": "User already exists"}, 409)

            user = User(username=username, is_active=True, email=email)
            db.session.add(user)
            db.session.commit()

            return make_response({'message': 'User created successfully'}, 201)
        except Exception as e:
            return make_response({"error": str(e)}, 500)
