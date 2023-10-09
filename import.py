import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

with open("books.csv") as books:
    rows = csv.DictReader(books)
    for row in rows:
        try:
            q = "INSERT INTO books(isbn, title, author, year) VALUES(:i, :t, :a, :y)"
            qi = text(q)
            db.execute(
                qi,
                {
                    "i": row["isbn"],
                    "t": row["title"],
                    "a": row["author"],
                    "y": row["year"],
                },
            )
        except:
            db.rollback()
            raise Exception("an error occurred when importing a book")
        else:
            db.commit()
