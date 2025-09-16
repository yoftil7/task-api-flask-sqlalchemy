from functools import wraps
from flask import abort
from flask_jwt_extended import get_jwt, verify_jwt_in_request


# RBAC access control
def role_required(*roles):
    """
    Decorator to restrict access based on user role(s).
    Example:
        @role_required("admin")
        def admin_route(): ...

        @role_required("admin", "manager")
        def multi_role_route(): ...
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in roles:
                abort(403, description="Forbidden: insufficient role")
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def admin_required():
    return role_required("admin")
