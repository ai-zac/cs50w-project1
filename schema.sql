CREATE TABLE books (
    isbn INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    book_id INTEGER,
    score INTEGER NOT NULL,
    content TEXT NOT NULL,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id)
    REFERENCES users (id)
    ON DELETE CASCADE,
    CONSTRAINT fk_book_id FOREIGN KEY (book_id)
    REFERENCES books (isbn)
    ON DELETE CASCADE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
