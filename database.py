from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import importlib

db = SQLAlchemy()
migrate = Migrate()


def init_database(app):
    db.init_app(app)
    migrate.init_app(app, db)
    # models_package = importlib.import_module('models')
    models_module = importlib.import_module('.models', 'models')
    for model_name in dir(models_module):
        if not model_name.startswith('_'):
            model_cls = getattr(models_module, model_name)
            if hasattr(model_cls, '__tablename__'):
                db.reflect(model_cls, extend_existing=True)
                db.create_all(bind=model_cls)

pass
