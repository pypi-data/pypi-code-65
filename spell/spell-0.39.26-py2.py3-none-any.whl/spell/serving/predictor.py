import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Union

from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from spell.serving.exceptions import InvalidPredictor
from spell.serving.types import (
    PredictorArgumentGenerator,
    PredictorMethod,
    PredictorMethodArguments,
)


class _ArgumentGenerator:
    __slots__ = ["json", "background_tasks", "request"]

    def __init__(
        self,
        json: Optional[str] = None,
        background_tasks: Optional[str] = None,
        request: Optional[str] = None,
    ) -> None:
        # json is a special attribute which, unlike the other two cannot be set by decorators
        self.json = json
        self.background_tasks = background_tasks
        self.request = request

    @classmethod
    def from_func(cls, func: PredictorMethod, min_args: int, is_staticmethod: bool):
        func_args = inspect.getfullargspec(func).args
        func_name = func.__name__
        annotations = cls._get_annotations(func, func_name)
        self_param = cls._get_self_param_name(
            func_name, func_args, annotations, min_args, is_staticmethod
        )
        # Check happens afer self param has been removed from func_args
        if len(func_args) < min_args:
            raise InvalidPredictor(f"{func_name} function must have at least {min_args} arguments")

        # Get all the args which do not have annotations
        # The set operation also ignores the return annotation
        unaccounted_args = set(func_args) - set(annotations)

        # Find all the params which are indicated using decorators
        params = getattr(func, "__injected_params__", cls())
        params.validate(self_param)

        # For all the params indicated in the decorators, ensure that it's in the set of
        # non-annotated params and remove it from that set because it has been accounted for
        for param in (params.background_tasks, params.request):
            if param is not None and param not in annotations:
                if param in unaccounted_args:
                    unaccounted_args.remove(param)
                else:
                    raise InvalidPredictor(
                        f"A decorator is expecting an argument named {param}, but it was not "
                        f"found in the signature for {func_name}"
                    )
        for param, type_ in annotations.items():
            if issubclass(type_, BackgroundTasks):
                if params.background_tasks and params.background_tasks != param:
                    raise InvalidPredictor(
                        f"Found both annotation and decorator for background tasks in signature for {func_name}"
                    )
                params.background_tasks = param
            elif issubclass(type_, Request):
                if params.request and params.request != param:
                    raise InvalidPredictor(
                        f"Found both annotation and decorator for full request in signature for {func_name}"
                    )
                params.request = param
        # Any args remaining in unaccounted args should the min params, like
        # (self, payload) for predict
        if len(unaccounted_args) > min_args:
            raise InvalidPredictor(
                f"Found ({unaccounted_args}) extra arguments in {func_name} function. "
                f"{func_name} expects at least {min_args} arguments. All additional "
                "arguments must have a type annotation or use decorators to indicate their "
                "use."
            )
        elif len(unaccounted_args) == min_args and min_args == 1:
            params.json = unaccounted_args.pop()
        return params

    @staticmethod
    def _get_annotations(func: PredictorMethod, func_name: str) -> Dict[str, Any]:
        annotations = func.__annotations__
        if len(set(annotations.values())) != len(annotations):
            raise InvalidPredictor(f"All annotations in {func_name} must be unique")
        return annotations

    @staticmethod
    def _get_self_param_name(
        func_name: str,
        func_args: List[str],
        annotations: Dict[str, Any],
        min_args: int,
        is_staticmethod: bool,
    ) -> Optional[str]:
        """Gets the self/cls param name and removes it from the
        funcion arguments list and the annotations dict"""
        # If the function is not a staticmethod, then we need to ignore the first parameter
        self_param = None
        if not is_staticmethod:
            if func_args:
                self_param = func_args.pop(0)
            elif min_args == 0:
                # example: health() rather than health(self)
                raise InvalidPredictor(
                    f"Expected a self or cls argument in {func_name} but found none. Add a self "
                    "or cls argument or mark as a staticmethod"
                )
            if self_param in annotations:
                annotations.pop(self_param)
        return self_param

    def validate(self, self_param: str) -> None:
        # Check that the param names don't refer to the same param
        if self.background_tasks is not None and self.background_tasks == self.request:
            raise InvalidPredictor(
                "Both request and background tasks are using the same parameter name "
                f"{self.request}"
            )

        # Check that the params do not refer to the self/cls param we are ignoring
        if self_param:
            if self.background_tasks == self_param:
                raise InvalidPredictor(f"Background tasks parameter cannot refer to {self_param}")
            if self.request == self_param:
                raise InvalidPredictor(f"Full request parameter cannot refer to {self_param}")

    async def make_arguments(self, request: Request) -> Union[PredictorMethodArguments, Response]:
        tasks = None
        kwargs = {}
        if self.background_tasks:
            tasks = BackgroundTasks()
            kwargs[self.background_tasks] = tasks
        if self.request:
            kwargs[self.request] = request
        if self.json:
            try:
                json_content = await request.json()
            except json.JSONDecodeError:
                return Response("Request must contain a JSON object", status_code=400), None
            kwargs[self.json] = json_content
        return kwargs, tasks


class BasePredictor:
    def health(self):
        return JSONResponse({"status": "ok"})

    @classmethod
    def validate(cls) -> None:
        cls.get_predict_argument_generator()
        cls.get_health_argument_generator()

    @classmethod
    def get_predict_argument_generator(cls) -> PredictorArgumentGenerator:
        return cls._create_argument_generator("predict", 1)

    @classmethod
    def get_health_argument_generator(cls) -> PredictorArgumentGenerator:
        return cls._create_argument_generator("health", 0)

    @classmethod
    def _create_argument_generator(cls, func_name, min_args: int) -> PredictorArgumentGenerator:
        """Creates a function which generates the arguments to either the predict or health
        methods. This is done to remove as much processing of the annotations and decorators out of
        the runtime of calling the method during a request.
        """
        func = cls._get_func_or_raise(func_name)
        is_staticmethod = cls._is_staticmethod(func_name)
        return _ArgumentGenerator.from_func(func, min_args, is_staticmethod).make_arguments

    @classmethod
    def _get_func_or_raise(cls, func_name: str) -> Callable:
        func = getattr(cls, func_name, None)
        if not func:
            raise InvalidPredictor(f'Required function "{func_name}" is not defined')
        if not callable(func):
            raise InvalidPredictor(f'"{func_name}" is defined, but is not a function')
        return func

    @classmethod
    def _is_staticmethod(cls, func_name: str) -> bool:
        # Unfortunately, getattr won't work properly here, so we need to directly use cls.__dict__,
        # but calling this on a subclass won't look in its base classes, which is a problem for the
        # health function. We could use cls.__base__, but this won't look further up a class
        # hierarchy, or mixins, so we need to manually traverse the entire method resolution order
        # (__mro__).
        cls_with_definition = next(
            (cls_ for cls_ in cls.__mro__ if cls_.__dict__.get(func_name) is not None), None
        )
        if cls_with_definition is None:
            # This should never happen because when this method is called,
            # getattr(cls, func_name) has returned a valid callable, so the user is doing
            # something seriously pathological here. We'll optimistically return False.
            return False
        return isinstance(cls_with_definition.__dict__[func_name], staticmethod)
