import os
import requests

from flask import Flask, session, render_template, flash, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # BASE DE DATOS INTERACTIVE
        user = db.execute("""SELECT id, username, hash FROM users WHERE username = ?""", username)

        if not user:
            flash("the user doesnt exist")
            return render_template("login.html")

        if check_password_hash(user[0]["hash"], password):
            session["user_id"] = user[0]["id"]
            return redirect("/")
        else:
            flash("username or password isnt correct")
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("The password isnt check")
            return render_template("register.html")

        hash = generate_password_hash(password)

        # BASE DE DATOS INTERACTIVE
        db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)", 
                   {"username": username, "hash": hash})
        db.commit()

        flash("The register was sucesfully")
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/")
def index():
    return render_template("home.html")
#     isbn='1632168146'
#     response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
#     print(response)
#     return response



if __name__ == "__main__":
    app.run()
