from flask import request, make_response, jsonify, Blueprint
from ..models import Project, Ticket, db
from ..utils.security_helper import SecurityHelper

ticket_bp = Blueprint('ticket', __name__)
