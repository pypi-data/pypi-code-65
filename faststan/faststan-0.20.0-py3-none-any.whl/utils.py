import importlib
import sys
from asyncio import get_event_loop, iscoroutinefunction
from pathlib import Path
from typing import Any, Callable

from loguru import logger


def _import(import_string: str):
    import_from, import_name = import_string.split(":")

    filepath = Path(import_from + ".py")
    if filepath:
        parent_dir = str(filepath.parent.absolute())
        logger.debug(
            f"Loading function '{import_name}' from file '{import_from}' located in directory '{parent_dir}'."
        )
        sys.path.append(parent_dir)
    else:
        logger.debug(f"Loading function {import_name} from module {import_from}.")
    module = importlib.import_module(import_from)
    return getattr(module, import_name)


async def always_run_async(function: Callable[..., Any], *args, **kwargs) -> Any:
    """Run a function and await its result if function is a coroutine"""
    # Call the function
    logger.debug(f"Executing function: {function.__name__}")
    result = function(*args, **kwargs)
    # If the function was a coroutine
    if iscoroutinefunction(function):
        logger.debug(f"Awaiting coroutine from {function.__name__}")
        # Await its result
        result = await result
    return result
