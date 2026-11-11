# Library Book Manager

A small web app for a librarian: manage books and track who has borrowed them.
AngularJS 1.8 frontend, Python Flask backend with SQLite.

## Requirements

- Python 3.10+

No Node.js or internet connection is needed; the frontend libraries
(AngularJS, Bootstrap) are included in `frontend/lib/`.

## Setup

### 1. Backend (Flask + SQLite)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python seed.py
```

Creates `backend/library.db` with 10 sample books. The script resets the
table, so it is safe to re-run.

### 3. Run the backend

```bash
python app.py
```

The API serves http://localhost:5001 with CORS enabled.

### 4. Run the frontend

In a second terminal:

```bash
cd frontend
python3 -m http.server 8080
```

Open http://localhost:8080 in a browser.

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Three tests: adding a book, borrowing the same book twice (409), and invalid
input (400).

## API

| Method | Path                      | Purpose                                    |
|--------|---------------------------|--------------------------------------------|
| GET    | `/api/books`              | List books; optional `search`, `category`  |
| POST   | `/api/books`              | Add a book                                 |
| GET    | `/api/books/<id>`         | One book                                   |
| PUT    | `/api/books/<id>`         | Edit a book                                |
| DELETE | `/api/books/<id>`         | Delete a book (409 while borrowed)         |
| POST   | `/api/books/<id>/borrow`  | Borrow; body: `{"borrower_name": "..."}`   |
| POST   | `/api/books/<id>/return`  | Return                                     |

Every response, including errors, is JSON, e.g. `{"error": "Title is required"}`.

## Project structure

```
backend/    Flask app (app.py), SQLite helpers (db.py), seed script, tests
frontend/   AngularJS app: list and form views, BookService (all HTTP calls)
```
