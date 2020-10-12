from dataclasses import dataclass

@dataclass(frozen = True)
class Author():
    last_name: str
    first_name: str

@dataclass(frozen = True)
class Date():
    year: str
    month: str
    day: str

@dataclass(frozen = True)
class Chris():
    quote: str
    author: Author
    date: Date
    context: str