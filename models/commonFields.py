from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class CommonFields(db.Model):
    __abstract__ = True
    uid = db.Column(db.String(36), default=str(uuid.uuid4()), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
