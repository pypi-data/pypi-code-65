import json

import pytest
from filmfestival.main import search_film
from filmfestival.main import query_firestore
from filmfestival.main import query_firestore_len
from filmfestival.main import save_film
from filmfestival.main import delete_content


def test_search_film():
    assert search_film("Harry Potter")["Year"] == "2011", "test ok"
    assert search_film("Harry Potter")["Released"] == "15 Jul 2011", "test ok"
    assert search_film("Harry Potter")["Runtime"] != "150 min"
    assert search_film("Star Wars")["Released"] != "25 May 1978", "test ok"
    assert search_film("Star Wars")["Genre"] == "Action, Adventure, Fantasy, Sci-Fi", "test ok"
    assert search_film("Star Wars")["Awards"] != "Won 5 Oscars. Another 51 wins & 28 nominations."


def test_query_firestore():
    assert query_firestore("Harry Potter and the Deathly Hallows: Part 2", "2011") == "David Yates"
    assert query_firestore("Star Wars: Episode IV - A New Hope", "1977") == "George Lucas"
    assert query_firestore("The Lord of the Rings: The Fellowship of the Ring", "2001") == "Peter Jackson"
    assert query_firestore("The Lord of the Rings: The Fellowship of the Ring", "2001") != "Steven Spielberg"
    assert query_firestore("Jurassic Park", "1993") == "Steven Spielberg"
    assert query_firestore("Jurassic Park", "1993") != "Peter Jackson"


def test_query_firestore_len():
    assert query_firestore_len("Jurassic Park") == "English, Spanish", "test ok"
    assert query_firestore_len("Back to the Future") == "English", "test ok"
    assert query_firestore_len("Jurassic Park") != "English, Italian, Spanish", "test ok"
    assert query_firestore_len("Star Wars: Episode IV - A New Hope") == "English", "test ok"
    assert query_firestore_len("Star Wars: Episode IV - A New Hope") != "Italian", "test ok"
    assert query_firestore_len("Million Dollar Baby") == "English, Irish", "test ok"
    assert query_firestore_len("Polisse") == "French, Italian, Romanian, Arabic", "test ok"


def test_save_film():
    f = open("integration_test_params.json", "r")
    content = f.read()
    content_json = json.loads(content)
    assert save_film(content_json), "test ok"


def test_delete_content():
    assert delete_content("Titanic"), "test ok"
    assert delete_content("Harry Potter and the Deathly Hallows: Part 2"), "test ok"
    assert delete_content("Star Wars: Episode IV - A New Hope"), "test ok"


if __name__ == '__main__':
    pytest.main()
