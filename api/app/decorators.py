from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from .models import Permission

# Permission required decorator.
def permission_required(perm):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(perm):
                flash('User account does not have the required permissions.')
                return redirect(url_for('main.dashboard'))
            return f(*args,**kwargs)
        return decorated_function
    return decorator

# Admin required decorator.
def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

#################################### ACTION ####################################
# Add additional decorators, if required.
################################################################################

def leader_required(f):
    return permission_required(Permission.ADD_USER)(f)
