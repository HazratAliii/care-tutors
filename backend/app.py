"""Library Book Manager API: Flask + SQLite.

Every response, including errors, is JSON.
Run with:  python app.py   (serves http://localhost:5001)
"""
import os
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import db

MIN_YEAR = 1900

# Sortable columns; values are SQL expressions, text ones sort case-insensitively.
SORTABLE_COLUMNS = {
    "title": "LOWER(title)",
    "author": "LOWER(author)",
    "category": "LOWER(category)",
    "published_year": "published_year",
    "created_at": "created_at",
}

app = Flask(__name__)
CORS(app)


# ------------------------------------------------------------------ database


def get_db():
    """One SQLite connection per request."""
    if "db" not in g:
        g.db = db.connect()
    return g.db


@app.teardown_appcontext
def close_db(exception):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


# ------------------------------------------------------------------- helpers


def fetch_book(book_id):
    """Return the book row with this id, or None."""
    return get_db().execute(
        "SELECT * FROM books WHERE id = ?", (book_id,)
    ).fetchone()


def book_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "category": row["category"],
        "published_year": row["published_year"],
        "is_borrowed": bool(row["is_borrowed"]),
        "borrower_name": row["borrower_name"],
        "created_at": row["created_at"],
    }


def error_response(message, status):
    return jsonify({"error": message}), status


def get_json_body():
    """Parse the request body as JSON; return None when it is not valid JSON."""
    return request.get_json(silent=True)


def current_year():
    return datetime.now().year


def validate_book(data):
    """Validate the book fields for create and edit.

    Returns an error message, or None when the payload is valid.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return "Title is required"

    author = data.get("author")
    if not isinstance(author, str) or not author.strip():
        return "Author is required"

    category = data.get("category", "")
    if not isinstance(category, str):
        return "Category must be a string"

    year = data.get("published_year")
    if not isinstance(year, int) or isinstance(year, bool):
        return "Published year must be an integer"
    if not MIN_YEAR <= year <= current_year():
        return f"Published year must be between {MIN_YEAR} and {current_year()}"

    return None


# ------------------------------------------------------------------- routes


@app.route("/api/books", methods=["GET"])
def list_books():
    """List books; optional query params: search, category, sort, order."""
    query = "SELECT * FROM books WHERE 1 = 1"
    params = []

    search = request.args.get("search", "").strip()
    if search:
        like = f"%{search.lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ?)"
        params += [like, like]

    category = request.args.get("category", "").strip()
    if category:
        query += " AND category = ?"
        params.append(category)

    sort_column = SORTABLE_COLUMNS.get(request.args.get("sort", ""))
    if sort_column:
        order = "DESC" if request.args.get("order", "").lower() == "desc" else "ASC"
        # The secondary id keeps the order stable when values are equal.
        query += f" ORDER BY {sort_column} {order}, id"
    else:
        query += " ORDER BY id"

    rows = get_db().execute(query, params).fetchall()
    return jsonify([book_to_dict(row) for row in rows])


@app.route("/api/books", methods=["POST"])
def create_book():
    data = get_json_body()
    if data is None:
        return error_response("Request body must be valid JSON", 400)

    error = validate_book(data)
    if error:
        return error_response(error, 400)

    now = datetime.now(timezone.utc).isoformat()
    cursor = get_db().execute(
        "INSERT INTO books (title, author, category, published_year, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (
            data["title"].strip(),
            data["author"].strip(),
            data.get("category", "").strip(),
            data["published_year"],
            now,
        ),
    )
    get_db().commit()

    return jsonify(book_to_dict(fetch_book(cursor.lastrowid))), 201


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    row = fetch_book(book_id)
    if row is None:
        return error_response("Book not found", 404)
    return jsonify(book_to_dict(row))


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    row = fetch_book(book_id)
    if row is None:
        return error_response("Book not found", 404)

    data = get_json_body()
    if data is None:
        return error_response("Request body must be valid JSON", 400)

    error = validate_book(data)
    if error:
        return error_response(error, 400)

    # Full replace of the editable fields; borrow state is managed by
    # the borrow/return endpoints, so it is left untouched here.
    get_db().execute(
        "UPDATE books SET title = ?, author = ?, category = ?, published_year = ?"
        " WHERE id = ?",
        (
            data["title"].strip(),
            data["author"].strip(),
            data.get("category", "").strip(),
            data["published_year"],
            book_id,
        ),
    )
    get_db().commit()

    return jsonify(book_to_dict(fetch_book(book_id)))


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    row = fetch_book(book_id)
    if row is None:
        return error_response("Book not found", 404)

    if row["is_borrowed"]:
        return error_response("Book is currently borrowed and cannot be deleted", 409)

    get_db().execute("DELETE FROM books WHERE id = ?", (book_id,))
    get_db().commit()
    return "", 204


@app.route("/api/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    data = get_json_body()
    if data is None:
        return error_response("Request body must be valid JSON", 400)

    borrower_name = data.get("borrower_name") if isinstance(data, dict) else None
    if not isinstance(borrower_name, str) or not borrower_name.strip():
        return error_response("Borrower name is required", 400)

    row = fetch_book(book_id)
    if row is None:
        return error_response("Book not found", 404)

    if row["is_borrowed"]:
        return error_response("Book is already borrowed", 409)

    get_db().execute(
        "UPDATE books SET is_borrowed = 1, borrower_name = ? WHERE id = ?",
        (borrower_name.strip(), book_id),
    )
    get_db().commit()

    return jsonify(book_to_dict(fetch_book(book_id)))


@app.route("/api/books/<int:book_id>/return", methods=["POST"])
def return_book(book_id):
    row = fetch_book(book_id)
    if row is None:
        return error_response("Book not found", 404)

    if not row["is_borrowed"]:
        return error_response("Book is not borrowed", 409)

    get_db().execute(
        "UPDATE books SET is_borrowed = 0, borrower_name = NULL WHERE id = ?",
        (book_id,),
    )
    get_db().commit()

    return jsonify(book_to_dict(fetch_book(book_id)))


# ------------------------------------------------------------ error handling


@app.errorhandler(HTTPException)
def handle_http_exception(exception):
    """Flask's own errors (404, 405, ...) are returned as JSON too."""
    return jsonify({"error": exception.description}), exception.code


@app.errorhandler(Exception)
def handle_unexpected_exception(exception):
    """Bad input must never surface as an HTML 500 page."""
    app.logger.exception("Unhandled error")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    db.init_db()
    # FLASK_HOST is set to 0.0.0.0 by Docker Compose so the API is reachable
    # from outside the container.
    app.run(host=os.environ.get("FLASK_HOST", "127.0.0.1"), port=5001, debug=True)
