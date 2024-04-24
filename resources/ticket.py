from .. import db
from flask import request, make_response, jsonify, Blueprint
from ..models import Project,Ticket

ticket_bp = Blueprint('ticket', __name__)