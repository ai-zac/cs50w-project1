<<<<<<< HEAD
=======
import os 
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    books = open("vuelos.csv")
    rows = csv.reader(books)

    db.execute()
    db.commit()

if __name__ == "__main__":
    main()
>>>>>>> 13397466578be6b40c37fff4276a75dc50ad7767
