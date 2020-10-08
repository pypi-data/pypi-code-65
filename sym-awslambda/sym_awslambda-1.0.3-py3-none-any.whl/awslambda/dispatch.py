import json

from google.protobuf import json_format

from sym.awslambda.errors import SymError
from sym.enums.service_pb2 import Service
from sym.messages.approval_pb2 import Approval
from sym.messages.dispatch_pb2 import Dispatch
from sym.messages.expiration_pb2 import Expiration
from sym.messages.options_pb2 import Options

_handlers = {}

_PROTOS = {
    "approve": Approval,
    "expire": Expiration,
    "options": Options,
}


def dispatch(event, context):
    """Dispatch the given event to the appropriate sym handler.

    Handlers are registered with the sym_action decorator.
    """
    try:
        dispatch = json_format.ParseDict(event, Dispatch())
        handler = _get_handler(dispatch.action)
        proto = _get_proto(dispatch.action, dispatch.payload.value)
        return handler(proto, context)
    except Exception as e:
        print("Unexpected exception:", str(e))
        return {"OK": False, "error": str(e)}


def _get_handler(action):
    handler = _handlers.get(action)
    if not handler:
        raise SymError(f"Unsupported action (no handler): {dispatch.action}")
    return handler


def _get_proto(action, value):
    proto_constructor = _PROTOS.get(action)
    if not proto_constructor:
        raise SymError(f"Unsupported action (no proto): {action}")
    proto = proto_constructor()
    proto.ParseFromString(value)
    return proto


def is_registered(action):
    """Check if a handler is registered for the given action."""
    return action in _handlers


def register(action, handler):
    """Register a handler for a Sym action.

    Only one handler is supported per action.
    """
    if action in _handlers:
        raise SymError(f"Already registered: {action}")

    if not action in _PROTOS:
        raise SymError(f"Unsupported action: {action}")

    print(f"Registering sym action: {action}")
    _handlers[action] = handler


def reset():
    _handlers.clear()
