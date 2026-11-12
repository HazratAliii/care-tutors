# Library Book Manager

A small web app for a librarian: manage books and track who has borrowed them.
AngularJS 1.8 frontend, Python Flask backend with SQLite.

## Requirements

- Python 3.10+ (backend, tests)
- Node.js (only for the frontend unit tests)

AngularJS and Bootstrap are included in `frontend/lib/`, so running the app
itself needs no internet connection.

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

Backend (3 pytest tests: add a book, borrow twice returns 409, invalid
input returns 400):

```bash
cd backend
source .venv/bin/activate
pytest
```

Frontend (1 Karma/Jasmine unit test for BookService, runs headless
Chrome):

```bash
cd frontend
npm install
npm test
```

## Docker Compose (optional)

With Docker running, one command starts both parts — the backend seeds
its database on startup:

```bash
docker compose up --build
```

The app is then at http://localhost:8080 and the API at
http://localhost:5001. Stop with `docker compose down`.

## API

| Method | Path                      | Purpose                                                       |
|--------|---------------------------|---------------------------------------------------------------|
| GET    | `/api/books`              | List books; optional `search`, `category`, `sort`, `order`    |
| POST   | `/api/books`              | Add a book                                                    |
| GET    | `/api/books/<id>`         | One book                                                      |
| PUT    | `/api/books/<id>`         | Edit a book                                                   |
| DELETE | `/api/books/<id>`         | Delete a book (409 while borrowed)                            |
| POST   | `/api/books/<id>/borrow`  | Borrow; body: `{"borrower_name": "..."}`                      |
| POST   | `/api/books/<id>/return`  | Return                                                        |

`sort` accepts `title`, `author`, `category`, `published_year` or
`created_at`; `order` is `asc` (default) or `desc`. Column headers in the
UI are clickable to sort.

Every response, including errors, is JSON, e.g. `{"error": "Title is required"}`.

## Project structure

```
backend/    Flask app (app.py), SQLite helpers (db.py), seed script, tests
frontend/   AngularJS app: list and form views, BookService (all HTTP calls)
```

## Notes

### What I would improve with more time

- Pagination for the book list on top of the current sorting.
- More frontend unit tests (controllers and form validation, not just the service).
- A proper modal dialog for the borrower's name instead of the native browser
  prompt, and inline error messages instead of alerts.
- Stricter input limits: maximum title/author length and a fixed category list.

### Use of AI tools

An AI coding assistant was used to help write the initial code for this
project: the backend, the frontend, the tests and this README. The commit
history shows how the project was built step by step, and every feature was
verified by running the pytest suite, calling the API directly and using the
app in a browser.
