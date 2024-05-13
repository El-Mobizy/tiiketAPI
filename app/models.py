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
PROJECT_ID = 'project.id'


class CommonFields(db.Model):
    __abstract__ = True
    uid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=True)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)

    def serialize(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(CommonFields, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self) -> str:
        return f"User {self.username}"


class UserToken(CommonFields, db.Model):
    __tablename__ = 'user_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)

    def __repr__(self):
        return f'<UserToken {self.token}>'


class Project(CommonFields, db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.now, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Project {self.title}>'

class Task(CommonFields, db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    completed_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Enum(Priority), default=Priority.LOW)
    status = db.Column(db.Enum(Status), default=Status.PENDING)
    progress = db.Column(db.Integer, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey(PROJECT_ID), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

class Role(CommonFields, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class Ticket(CommonFields, db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(Status), default=Status.PENDING)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM)
    project_id = db.Column(db.Integer, db.ForeignKey(PROJECT_ID), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)

    def __repr__(self):
        return f'<Ticket {self.title}>'


class Team(CommonFields, db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=True)
    description = db.Column(db.String(255), nullable=True)
    members = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(PROJECT_ID), nullable=False)

    def __repr__(self):
        return f"<Team {self.name}>"


class AppLog(db.Model):
    __tablename__ = 'app_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AppLog {self.action}>'


class Tag(CommonFields, db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Tag {self.name}>"


class TagEntity(CommonFields, db.Model):
    __tablename__ = 'tag_entity'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    entity = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Tag {self.name}>"
