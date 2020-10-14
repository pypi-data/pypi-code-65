from typing import Callable, List, Optional, Tuple, Type
from inspect import signature, Signature, Parameter
from pydantic import BaseModel

from nats.aio.client import Client as NATS
from nats.aio.client import Msg as NATSMsg
from stan.aio.client import Client as STAN
from stan.aio.client import Msg as STANMsg

from .models import Subject


def check_pydantic_model(_type: Type) -> bool:
    """Check if given type is a pydantic model.

    Arguments:
    -----------
        _type: The type to check.

    Return:
    -----------
        A boolean indicating if given type is a pydantic model or not.
    """
    try:
        return issubclass(_type, BaseModel)
    except TypeError:
        return False


def inspect_subscription_callback(
    function: Callable[..., Optional[BaseModel]], allow_no_return: bool = False,
) -> Tuple[Type[BaseModel], Type[BaseModel], List[Tuple[str, Parameter]]]:
    """Inspect a function, validate its signature and return its input model and output model as well as extra parameters.

    This function is mostly used by the subscribe and reply wrappers.

    Arguments:
    -----------
        function: A callable that expects a pydantic model and returns a pydantic model.

    Raises:
    -----------
        TypeError: Invalid function signature. More details will be available in error message.
    """
    # First with need the function signature
    s = signature(function)

    # From there we can get a pseudo-dict of parameters
    parameters = s.parameters
    # We can use .items() to iterate over tuple (parameter_name, parameter_object)
    # Let's store those tuples into a list
    iter_params = list(s.parameters.items())
    # Evaluating a list as a boolean return False if the list is empty, else True
    if not iter_params:
        # If the list if empty: raises a TypeError
        raise TypeError(
            f"NATS or STAN subscriptions must at least accept pydantic model as parameter."
        )
    # If we reach this point list is not empty
    # Let's fetch the first argument and remove it from the list using pop method
    main_arg_name, main_arg_param = iter_params.pop(0)
    # Let's get the annotation
    main_arg_annotation = main_arg_param.annotation
    # Check it's a valid pydantic model
    if not check_pydantic_model(main_arg_annotation):
        raise TypeError(
            f"Parameter {main_arg_name} must be typed as a valid pydantic model. "
            f"Given annotation for {main_arg_name} is {main_arg_annotation}."
        )
    # Let's check the return annotation
    return_annotation = s.return_annotation
    if not check_pydantic_model(return_annotation):
        if not allow_no_return:
            raise TypeError(
                f"Function return must be typed as a valid pydantic model. "
                f"Given annotation for return is {return_annotation}."
            )
    return main_arg_annotation, return_annotation, iter_params


def inspect_extra_params(
    iter_params: List[Tuple[str, Parameter]],
) -> Tuple[bool, str, bool, str]:
    """Inspect a list of parameters to determine if the NATS/STAN message or subject should be injected
    as arguments when executing the callback.

    Arguments:
    -----------
        iter_params: A list of tuple (parameter_name, parameter).

    Returns:
    -----------
        This function returns 4 values:
          - include_message: Whether the message should be included or not.
          - message_parameter: The name of the parameter that will receive the message as value.
          - include_subject: Whether the subject should be included or not.
          - subject_parameter: The name of the parameter that will receive the subject as value.

    Raises:
    -----------
        ValueError: This error most likely indicates that either that two arguments of same type (either subject or message) are present in given list.
        TypeError: This error indicates that a parameter with unsupported type is present in given list.
    """

    # Initialize a variable include_message to False
    include_message = False
    message_parameter = ""
    # Initialize a variable include_subject to False
    include_subject = False
    subject_parameter = ""
    # Loop will run until iter_params is empty
    while iter_params:
        # Fetch and remove each parameter fro mthe list using pop method
        name, parameter = iter_params.pop(0)
        # Check if parameters are of type STANMsg or NATSMsg
        if parameter.annotation in (STANMsg, NATSMsg):
            # If there was already a parameter with one of those types raise an error
            if include_message:
                raise ValueError(
                    "It is not allowed to specify more than one parameter with type STANMsg or NATSMsg."
                )
            include_message = True
            message_parameter = name
            # Else continue so that code below is skipped
            continue
        # Check if parameter is of type subject
        if parameter.annotation in (Subject,):
            # As for message, we don't want to have two parameters of same type
            if include_subject:
                raise ValueError(
                    "It is not allowed to specify more than one parameter with type Subject."
                )
            include_subject = True
            subject_parameter = name
            continue
        # Check if parameters are of type
        # For the moment we do not support other parameters types so we raise an error
        raise TypeError(f"Unsupported argument: {name} with type: {parameter}.")

    return include_message, message_parameter, include_subject, subject_parameter
