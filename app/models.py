from datetime import datetime
import uuid
from app.extensions import db
from enum import Enum


class Status(Enum):
    PENDING = 'Pending'
    RESOLVED = 'Resolved'
    ON_HOLD = 'On hold'
    ASSIGNED = 'Assigned'
    CANCELLED = 'Cancelled'


class ProjectStatus(Enum):
    ACTIVE = 'Active'
    ON_HOLD = 'On hold'
    COMPLETED = 'Completed'


class Priority(Enum):
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'


USER_ID = 'user.id'


class CommonFields(db.Model):
    __abstract__ = True
    uid = db.Column(db.String(36), default=str(uuid.uuid4()), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)


class UserToken(CommonFields):
    __tablename__ = 'user_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)


class Ticket(CommonFields):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(Status), default=Status.PENDING)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)


class AppLog(CommonFields):
    __tablename__ = 'app_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Team(CommonFields):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=True)
    description = db.Column(db.String(255), nullable=True)
    members = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)


class Project(CommonFields):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.now, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)


class TagEntity(db.Model):
    __tablename__ = 'tag_entity'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    entity = db.Column(db.String(50), nullable=False, unique=True)
