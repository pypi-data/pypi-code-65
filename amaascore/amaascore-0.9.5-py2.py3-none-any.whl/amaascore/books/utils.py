from __future__ import absolute_import, division, print_function, unicode_literals
import inspect
from dateutil.parser import parse
from decimal import Decimal

from amaascore.books.book import Book


def json_to_book(json_book):
    book = Book(**json_book)
    return book
