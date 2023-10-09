from functools import wraps
from flask import session, redirect, flash, url_for

def login_required(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        if "user_id" not in session:
            flash("You need login before")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorate


def book_tuple_to_dict(d):
    keys = ["isbn", "title", "author", "year"]
    b = {}
    for i in range(0, len(keys)):
        b[keys[i]] = d[i]

    return b
