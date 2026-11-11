"""Tests for the books API.

The three scenarios required by the task:
1. add a book
2. borrowing the same book twice returns 409
3. invalid input returns 400
"""
import pytest

import db
from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A test client backed by a fresh temporary database."""
    monkeypatch.setenv("LIBRARY_DB", str(tmp_path / "library.db"))
    db.init_db()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_book(client):
    response = client.post(
        "/api/books",
        json={
            "title": "The Hobbit",
            "author": "J. R. R. Tolkien",
            "category": "Fiction",
            "published_year": 1937,
        },
    )
    assert response.status_code == 201
    book = response.get_json()
    assert book["title"] == "The Hobbit"
    assert book["is_borrowed"] is False

    listing = client.get("/api/books").get_json()
    assert any(item["id"] == book["id"] for item in listing)


def test_borrowing_the_same_book_twice_returns_conflict(client):
    book = client.post(
        "/api/books",
        json={
            "title": "Dune",
            "author": "Frank Herbert",
            "category": "Fiction",
            "published_year": 1965,
        },
    ).get_json()

    first = client.post(
        f"/api/books/{book['id']}/borrow", json={"borrower_name": "Sara"}
    )
    assert first.status_code == 200
    assert first.get_json()["borrower_name"] == "Sara"

    second = client.post(
        f"/api/books/{book['id']}/borrow", json={"borrower_name": "Karim"}
    )
    assert second.status_code == 409
    assert "error" in second.get_json()


def test_add_book_with_invalid_input_returns_400(client):
    response = client.post(
        "/api/books",
        json={"title": "", "author": "Someone", "published_year": 2050},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"
