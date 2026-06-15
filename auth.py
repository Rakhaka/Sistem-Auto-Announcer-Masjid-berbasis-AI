from functools import wraps
from flask import session, redirect, url_for, request

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
