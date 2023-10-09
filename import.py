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


def main():
    with open("books.csv") as books:
        rows = csv.DictReader(books)
        for row in rows:
            db.execute(
                text(
                    "INSERT INTO books(isbn, title, author, year) VALUES (:isbn, :title, :author, :year)"
                ),
                {
                    "isbn": row["isbn"],
                    "title": row["title"],
                    "author": row["author"],
                    "year": row["year"],
                },
            )
            db.commit()


if __name__ == "__main__":
    main()
