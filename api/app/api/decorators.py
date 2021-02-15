from functools import wraps
from flask import g, jsonify
from .errors import forbidden
from ..models import User, Family, Role, Permission

# Decorator to determine user permissions.
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# This decorator will ensure only leaders have permission to do specific functions.
def leader_required(f):
    return permission_required(Permission.ADD_USER)(f)


# This decorator will ensure only admins have permission to do specific functions.
def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


# This decorator will check to see is the session current_user is assigned, and
#   will return a 401 error code if they are not assigned.
def login_required_dec(login):
    def decorate_it(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if g.current_user == None:
                response = jsonify({'message':'Unauthorized'})
                response.status_code = 401
                return response
            return f(*args, **kwargs)
        return decorated_function
    return decorate_it

def login_required(f):
    return login_required_dec('nothing')(f)
