from functools import wraps

from flask import current_app, g, session

from beront.modules.identity.domain.policies import PERMISSIONS
from beront.shared.domain.errors import Forbidden, Unauthorized


def require_auth(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            g.admin = current_app.extensions["beront"].identity.authenticate(session.get("sid"))
        except Unauthorized:
            session.clear()
            raise
        g.permissions = PERMISSIONS
        return function(*args, **kwargs)

    wrapper.requires_auth = True
    return wrapper


def require_permission(permission):
    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not getattr(g, "admin", None):
                raise Unauthorized()
            if permission not in getattr(g, "permissions", ()):
                raise Forbidden()
            return function(*args, **kwargs)

        wrapper.required_permission = permission
        return wrapper

    return decorate
