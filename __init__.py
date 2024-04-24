import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
from .utils.custom_converters import UuidConverter


load_dotenv()

app = Flask(__name__)
app.url_map.converters['uuid'] = UuidConverter
api_bp = Blueprint('api', __name__)

db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET')

db.init_app(app)

from .resources.project import project_bp
from .resources.ticket import ticket_bp
app.register_blueprint(project_bp)
app.register_blueprint(ticket_bp)

if __name__ == '__main__':
    app.run(debug=True)