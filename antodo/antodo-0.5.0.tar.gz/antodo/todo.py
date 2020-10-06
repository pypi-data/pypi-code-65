from dataclasses import asdict
from dataclasses import dataclass
import os
import json
from typing import List, Optional

import click
import safer

import antodo.config as c


@dataclass
class Todo:
    content: str
    urgent: bool
    current: Optional[bool] = False

    def __str__(self) -> str:
        return self.content

    def toggle_urgent(self):
        self.urgent = not self.urgent

    def toggle_current(self):
        self.current = not self.current

    def get_color(self):
        if self.current:
            return c.CURRENT_COLOR
        if self.urgent:
            return c.URGENT_COLOR
        return c.DEFAULT_COLOR


class Todos:
    def __init__(self):
        self._loader = TodosLoader()
        self._todos: list = self._loader.load_todos()

    def add_todo(self, content: str, urgent: bool):
        self._todos.append(Todo(content, urgent))

    def remove_todos(self, indexes_to_remove):
        self._todos = [todo for index, todo in enumerate(self._todos) if index not in indexes_to_remove]

    def save(self):
        self._loader.save_todos(self)

    def to_json(self):
        return list(map(lambda todo: asdict(todo), self._todos))

    def show(self):
        for index, todo in enumerate(self._todos, 1):
            click.secho(f"{index}. {todo.content}", fg=todo.get_color())

    def clear(self):
        self._todos = []

    def __getitem__(self, index):
        return self._todos[index]

    def __setitem__(self, index, value):
        self._todos[index] = value

    def __bool__(self):
        return bool(self._todos)

    def __len__(self):
        return len(self._todos)

    def __iter__(self):
        return iter(self._todos)


class TodosLoader:
    DEFAULT_TODOS: dict = {"todos": []}

    def __init__(self):
        self.todos_path = c.TODOS_JSON_PATH
        self.todos_dir = c.TODOS_DIR

    def load_todos(self) -> List[Todo]:
        todos_json = self._get_or_create_todos()
        todos = list(map(lambda todo: Todo(**todo), todos_json["todos"]))
        return todos

    def _get_or_create_todos(self) -> dict:
        if os.path.exists(self.todos_path):
            with open(self.todos_path) as file:
                return json.load(file)

        os.makedirs(self.todos_dir, exist_ok=True)
        with safer.open(self.todos_path, "w") as file:
            json.dump(self.DEFAULT_TODOS, file)

        return self.DEFAULT_TODOS

    def save_todos(self, todos: Todos):
        with safer.open(self.todos_path, "w") as file:
            json.dump({"todos": todos.to_json()}, file)
