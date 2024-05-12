from app.resources.project import project_api
from app.resources.task import task_api
from app.resources.auth import authentication_webhook_ns


def setup_namespaces(api):
    api.add_namespace(authentication_webhook_ns)
    api.add_namespace(project_api)
    api.add_namespace(task_api)
    return api.namespaces
