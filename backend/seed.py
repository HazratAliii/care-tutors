"""Seed the library database with 10 sample books.

Running this script resets the books table, so it is safe to re-run.
"""
from datetime import datetime, timezone

import db

SAMPLE_BOOKS = [
    # (title, author, category, published_year)
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 1925),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", 1960),
    ("1984", "George Orwell", "Fiction", 1949),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction", 1967),
    ("A Brief History of Time", "Stephen Hawking", "Science", 1988),
    ("The Selfish Gene", "Richard Dawkins", "Science", 1976),
    ("Cosmos", "Carl Sagan", "Science", 1980),
    ("Silent Spring", "Rachel Carson", "Science", 1962),
    ("The Guns of August", "Barbara W. Tuchman", "History", 1962),
    ("A People's History of the United States", "Howard Zinn", "History", 1980),
]


def main():
    now = datetime.now(timezone.utc).isoformat()
    with db.connect() as connection:
        connection.executescript(db.SCHEMA)
        connection.execute("DELETE FROM books")
        connection.executemany(
            "INSERT INTO books (title, author, category, published_year, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            [(title, author, category, year, now)
             for title, author, category, year in SAMPLE_BOOKS],
        )
    print(f"Seeded {len(SAMPLE_BOOKS)} books into {db.get_db_path()}")


if __name__ == "__main__":
    main()
