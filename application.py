import os
import secrets
import requests 
from flask import Flask, jsonify, session, render_template, flash, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from login_required import login_required

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



@app.route("/")
def index():
    return render_template("home.html", session=session)


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

        db.execute(text("""INSERT INTO usuarios(nombre, contrasena) 
                    VALUES(:nombre, :contrasena)"""), 
                   {"nombre": username, "contrasena": hash}) 
        db.commit()

        flash("The register was sucesfully")
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # BASE DE DATOS INTERACTIVE
        user = db.execute(text("""SELECT id, nombre, contrasena FROM usuarios 
                              WHERE nombre = :username"""), 
                         {"username": username}).fetchone()

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


@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        rqsearch = request.form.get("search")

        data = db.execute(text(f"""
                    SELECT  titulo ,
                            isbn   FROM libros 
                    WHERE   isbn   LIKE '%{rqsearch}%' OR 
                            titulo LIKE '%{rqsearch}%' OR
                            autor  LIKE '%{rqsearch}%' """)).fetchall()

        if data == []:
            flash("No se encontraron resultados, especifica bien las mayusculas o minusculas")
            return redirect("/")
        else:

            flash("Busqueda correcta")
            return render_template("search.html", dataset=data)


@app.route("/libro_review", methods=["POST", "GET"])
@login_required
def libro_review():
    # Esto se podria mejorar 
    key_ratings_api = ["averageRating", "ratingsCount"]
    list_columns_libros = ["id", "isbn", "title", "author", "year"]
# * = id, isbn, title, author, year
    book_data = {}
    reseñas_libro = []

    if request.method == "POST":
        isbn = request.form.get("isbn")
        book_db = db.execute(text(f""" SELECT * FROM libros WHERE isbn = '{isbn}' """)).fetchone()
        ratings_book = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json() 

        for i in range(0, len(list_columns_libros), 1):
            book_data[list_columns_libros[i]] = book_db[i]

        # Algunos libros en la API no tienen reseñas 
        for key in key_ratings_api:
            try:
                book_data[key] = ratings_book["items"][0]["volumeInfo"][key]
            except KeyError:
                book_data[key] = "Sin registro"

        reseñas_db = db.execute(text(f"""SELECT  puntuaje, reseña, usuarios.nombre FROM reseñas
                                    JOIN usuarios ON reseñas.usuarios_id = usuarios.id
                                    WHERE   libros_id = '{book_data['id']}'""")).fetchall()
        
        for element in reseñas_db:
            reseñas_libro.append({"puntuaje": element[0], "reseña": element[1], "nombre": element[2]})

        return render_template("libro.html", dataset=book_data, reseñas=reseñas_libro)


@app.route("/reseñas_post", methods=["POST", "GET"])
@login_required
def reseñas_post():
    if request.method == "POST":
        puntuaje = request.form.get("puntuaje")
        reseña = request.form.get("reseña")
        id_book = request.form.get("id")

        comprobante = db.execute(text(f"SELECT * FROM reseñas WHERE usuarios_id = '{ session['user_id'] }' AND libros_id = '{id_book}' ")).fetchone()
        if comprobante is None:
            db.execute(text(f"INSERT INTO reseñas(puntuaje, reseña, usuarios_id, libros_id) VALUES('{puntuaje}', '{reseña}', '{session['user_id']}', '{id_book}')"))
            db.commit()
        else:
            flash("No puedes ingresar más de una reseña o puntuaje al mismo libro")    
        return redirect("/")


@app.route("/api/<isbn>")
@login_required
def api(isbn):
    key_ratings_api = ["averageRating", "ratingsCount"]
    list_columns_libros = ["id", "isbn", "title", "author", "year"]
    book_data = {}

    book_db = db.execute(text(f""" SELECT * FROM libros WHERE isbn = '{isbn}' """)).fetchone()
    ratings_book = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json() 

    for i in range(0, len(list_columns_libros), 1):
        book_data[list_columns_libros[i]] = book_db[i]

    # Algunos libros en la API no tienen reseñas 
    for key in key_ratings_api:
        try:
            book_data[key] = ratings_book["items"][0]["volumeInfo"][key]
        except KeyError:
            book_data[key] = "Sin registro"

    return jsonify( title=book_data["title"],
                    author=book_data["author"],
                    year=book_data["year"],
                    isbn=book_data["isbn"],
                    review_count=book_data["ratingsCount"],
                    average_score=book_data["averageRating"]
                    )


#     isbn='1632168146' 
#     response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
#     print(response)
#     return response




