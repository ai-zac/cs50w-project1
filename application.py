import os
import secrets
import requests
from flask import Flask, session, render_template, flash, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from tools import book_tuple_to_dict, login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to ufrom required import login_requiredse filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secrets.token_hex()

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("home.html", session=session)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        c = request.form.get("confirmation")

        if p != c:
            flash("The password isnt check")
            return render_template("register.html")

        hash = generate_password_hash(p)

        qi = text("INSERT INTO users(username, password) VALUES(:nombre, :contrasena)")
        db.execute(qi, {"nombre": u, "contrasena": hash})
        db.commit()
        flash("The register was sucesfully")

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        qs = text("SELECT * FROM users WHERE username = :u")
        user = db.execute(qs, {"u": u}).fetchone()

        if not user:
            flash("the user doesn't exist")
            return render_template("login.html")

        if check_password_hash(user[2], p):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            flash("username or password isn't correct")
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

        qs = text(
            """SELECT
                   title,
                   isbn
               FROM books
               WHERE
                   isbn LIKE :r
                   OR title LIKE :r
                   OR author LIKE :r"""
        )
        data = db.execute(qs, {"r": "%" + rqsearch + "%"}).fetchall()
        if data == []:
            flash(
                """There was an error in the search, please specify the
                upper and lower case letters correctly"""
            )
            return redirect("/")

        books = [list(item) for item in data]

        for i in range(0, len(books)):
            url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + books[i][1]
            api = requests.get(url).json()
            img = api["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            books[i].append(img)

        flash("Successful search")
        return render_template("search.html", dataset=books)
    return redirect("/")


@app.route("/book/<isbn>", methods=["POST", "GET"])
@login_required
def libro_review(isbn):
    qs = text("SELECT * FROM books WHERE isbn = :i")
    book_db = db.execute(qs, {"i": isbn}).fetchone()
    book_data = book_tuple_to_dict(book_db) # Sort db query results into dict

    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    api = requests.get(url).json()
    api = api["items"][0]["volumeInfo"]
    book_data["img"] = api["imageLinks"]["thumbnail"]
    # Then add api ratings into book dict
    api_keys = ["averageRating", "ratingsCount"]
    for key in api_keys:
        try:
            book_data[key] = api[key]
        # Some books doesn't have api ratings
        except KeyError:
            book_data[key] = "No found"

    qs = text(
        """
                SELECT r.score,
                       r.content,
                       u.username
                FROM   reviews AS r
                       join users AS u
                         ON r.user_id = u.id
                WHERE  r.book_id = :b
            """
    )
    reviews_db = db.execute(qs, {"b": isbn}).fetchall()
    # Sort books reviews into a dict
    reviews_book = []
    for element in reviews_db:
        reviews_book.append(
            {"puntuaje": element[0], "reseña": element[1], "nombre": element[2]}
        )

    return render_template("libro.html", dataset=book_data, reviews=reviews_book)


@app.route("/rating/add", methods=["POST"])
@login_required
def add_rating():
    i = request.form.get("isbn")

    # Check that only 1 review per book can be sent.
    qs = text("SELECT * FROM reviews WHERE user_id = :s AND book_id = :i")
    check = db.execute(qs, {"s": session["user_id"], "i": i}).fetchone()
    if check != []:
        flash("Only one review per book is allowed")
        redirect(f"/book/{i}")

    # Save review
    s = request.form.get("score")
    c = request.form.get("content")
    qi = text(
        "INSERT INTO reviews(score, content, user_id, book_id) VALUES(:s, :c, :u, :b)"
    )
    db.execute(qi, {"s": s, "c": c, "u": session["user_id"], "b": i})
    db.commit()
    return redirect(f"/book/{i}")


@app.route("/api/<isbn>")
@login_required
def api(isbn):
    # Sort db query results into dict
    qs = text("SELECT * FROM books WHERE isbn = :i")
    book_db = db.execute(qs, {"i": isbn}).fetchone()
    book_data = book_tuple_to_dict(book_db)

    # Some books doesn't have api ratings
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    api = requests.get(url).json()
    api_value_keys = ["averageRating", "ratingsCount"]
    for key in api_value_keys:
        try:
            book_data[key] = api["items"][0]["volumeInfo"][key]
        except KeyError:
            book_data[key] = "No found"

    return {
        "title": book_data["title"],
        "author": book_data["author"],
        "year": book_data["year"],
        "isbn": book_data["isbn"],
        "review_count": book_data["ratingsCount"],
        "average_score": book_data["averageRating"],
    }
