import os
import secrets
import requests

from flask import Flask, session, render_template, flash, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to ufrom required import login_requiredse filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secrets.token_hex()

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))  
db = scoped_session(sessionmaker(bind=engine))

prueba = db.execute("SELECT * from libros WHERE año_publicacion = 1000").fetchone()
print(prueba)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # BASE DE DATOS INTERACTIVE
        user = db.execute("SELECT id, nombre, contrasena FROM usuarios WHERE nombre = :username", {"username": username}).fetchone()

        if not user:
            flash("the user doesnt exist")
            return render_template("login.html")

        if check_password_hash(user[2], password):
            session["user_id"] = user[0]
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

        db.execute("INSERT INTO usuarios(nombre, contrasena) VALUES(:nombre, :contrasena)", 
                   {"nombre": username, "contrasena": hash})
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



