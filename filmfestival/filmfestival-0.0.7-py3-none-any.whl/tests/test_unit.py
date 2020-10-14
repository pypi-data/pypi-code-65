import pytest
from filmfestival.main import format_title
from filmfestival.main import compose_url


def test_format_title():
    assert format_title("harry potter") == "harry+potter", "test ok"
    assert format_title("HaRRy PoTTER") == "harry+potter", "test ok"
    assert format_title("Harry Potter") != "harry potter", "test ok"
    assert format_title("      Harry Potter    ") == "harry+potter", "test ok"
    assert format_title("Harry Potter        ") == "harry+potter", "test ok"
    assert format_title("Harry   Potter") != "harry+potter", "test ok"
    assert format_title("    HaRRy PoTTEr    ") == "harry+potter", "test ok"


def test_compose_url():
    assert compose_url("harry+potter") == "http://www.omdbapi.com/?apikey=9ea40129&t=harry+potter", "test ok"
    assert compose_url("harry+potter") != "http://www.omdbapi.com/?t=harry+potter", "test ok"
    assert compose_url("HARRY+POTTER") == "http://www.omdbapi.com/?apikey=9ea40129&t=HARRY+POTTER", "test ok"



if __name__ == '__main__':
    pytest.main()
