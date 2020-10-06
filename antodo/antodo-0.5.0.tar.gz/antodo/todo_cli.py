import contextlib
from typing import List

import click

from antodo.todo import Todos
from antodo.todo_editor import TodoEditor
from . import __version__


@click.group()
@click.version_option(__version__, "--version", "-v")
def todo_cli():
    """simple another todo CLI app"""


@todo_cli.command(help="show current todos")
def show():
    todos = Todos()
    if todos:
        todos.show()
    else:
        click.echo("No todos found")


@todo_cli.command(help="add todo")
@click.argument("content", nargs=-1, type=click.STRING)
@click.option("--urgent", "-u", is_flag=True, help="set todo as urgent")
def add(content: List[str], urgent: bool):
    content_str: str = " ".join(content)
    if not content_str:
        raise click.BadArgumentUsage("cant add empty todo")
    with todos_operation() as todos:
        todos.add_todo(content_str, urgent)


@todo_cli.command(help="removes todo")
@click.argument("indexes", nargs=-1, type=click.INT)
def remove(indexes: List[int]):
    with todos_operation() as todos:
        indexes_to_remove = filter_indexes(todos, indexes)
        todos.remove_todos(indexes_to_remove)
        click.echo(f"deleted todos: {[i+1 for i in indexes_to_remove]}")


@todo_cli.command(help="toggle todo as urgent")
@click.argument("indexes", nargs=-1, type=click.INT)
def urgent(indexes: List[int]):
    with todos_operation() as todos:
        indexes_to_set = filter_indexes(todos, indexes)
        for index in indexes_to_set:
            todos[index].toggle_urgent()


@todo_cli.command(help="toggle todo as current")
@click.argument("indexes", nargs=-1, type=click.INT)
def current(indexes: List[int]):
    with todos_operation() as todos:
        indexes_to_set = filter_indexes(todos, indexes)
        for index in indexes_to_set:
            todos[index].toggle_current()


@todo_cli.command(help="clear current todos")
@click.option("-y", "confirm", is_flag=True, help="clear without confirm promt")
def clear(confirm: bool):
    if confirm or click.confirm("Delete all todos?"):
        with todos_operation() as todos:
            todos.clear()


@todo_cli.command(help="clear current todos")
@click.argument("index", type=click.INT)
def edit(index: int):
    with todos_operation() as todos:
        todo = todos[index - 1]

        editor = TodoEditor(todo)
        new_content = editor.get_new_todo_content()
        todo.content = new_content

        todos[index - 1] = todo


@contextlib.contextmanager
def todos_operation():
    todos = Todos()
    try:
        yield todos
    except Exception as err:
        raise click.ClickException(str(err))
    else:
        todos.save()
    finally:
        todos.show()


def filter_indexes(todos: Todos, indexes: List[int]):
    return [i - 1 for i in indexes if i - 1 < len(todos)]
