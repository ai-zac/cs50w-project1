from functools import wraps
from flask import session, redirect, flash, url_for

def login_required(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        if not "user_id" in session:
            flash("Necesitas logearte primero")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorate