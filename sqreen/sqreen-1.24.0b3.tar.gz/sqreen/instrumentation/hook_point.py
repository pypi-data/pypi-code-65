# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Contains the hook_point, the code actually executed in place of
application code
"""
import logging
import sys

from .._vendors.wrapt import FunctionWrapper
from ..constants import ACTIONS, LIFECYCLE_METHODS, VALID_ACTIONS_PER_LIFECYCLE
from ..exceptions import ActionBlock, ActionRedirect, AttackBlocked
from ..execute_callbacks import execute_callbacks, valid_args
from ..runtime_storage import runtime
from .helpers import guard_call

LOGGER = logging.getLogger(__name__)


def execute_pre_callbacks(
    key, strategy, instance, args=None, kwargs=None, storage=runtime,
    override_budget=None
):
    """ Execute pre_callbacks. Pre callbacks will receive these arguments:
    (instance, args, kwargs)
    """
    pre_callbacks = strategy.get_pre_callbacks(key)
    if pre_callbacks:
        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            pre_callbacks,
            LIFECYCLE_METHODS["PRE"],
            instance,
            args,
            kwargs,
            storage=storage,
            override_budget=override_budget,
            valid_actions=VALID_ACTIONS_PER_LIFECYCLE[LIFECYCLE_METHODS["PRE"]],
        )
    return {}


def execute_failing_callbacks(
    key, strategy, instance, exc_info, args=None, kwargs=None, storage=runtime,
    override_budget=None
):
    """ Execute failing_callbacks. Failing callbacks will receive these arguments:
    (instance, args, kwargs, exc_info=exc_info)
    """
    failing_callbacks = strategy.get_failing_callbacks(key)
    if failing_callbacks:
        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            failing_callbacks,
            LIFECYCLE_METHODS["FAILING"],
            instance,
            args,
            kwargs,
            exc_info=exc_info,
            storage=storage,
            override_budget=override_budget,
            valid_actions=VALID_ACTIONS_PER_LIFECYCLE[LIFECYCLE_METHODS["FAILING"]],
        )
    return {}


def execute_post_callbacks(
    key, strategy, instance, result, args=None, kwargs=None, storage=runtime,
    override_budget=None
):
    """ Execute post_callbacks. Post callbacks will receive these arguments:
    (instance, args, kwargs, result=result)
    """
    post_callbacks = strategy.get_post_callbacks(key)
    if post_callbacks:
        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            post_callbacks,
            LIFECYCLE_METHODS["POST"],
            instance,
            args,
            kwargs,
            result=result,
            storage=storage,
            override_budget=override_budget,
            valid_actions=VALID_ACTIONS_PER_LIFECYCLE[LIFECYCLE_METHODS["POST"]],
        )
    return {}


def hook_point_wrapper(strategy, hook_name, hook_method, storage=runtime):
    """ Execute the original method and pre/post/failing callbacks
    If an exception happens, create a RemoteException, call
    callback.exception_infos for more debugging infos and send it via
    the provided queue.
    """
    key = (hook_name, hook_method)

    def wrapper(wrapped, instance, args, kwargs):
        strategy.before_hook_point()

        # Call pre callbacks
        action = execute_pre_callbacks(
            key,
            strategy,
            instance,
            args,
            kwargs,
            storage=storage
        )

        if action.get("status") == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )
            raise AttackBlocked(action.get("rule_name"))
        elif action.get("status") == ACTIONS["ACTION_BLOCK"]:
            LOGGER.debug(
                "Action %s blocked the request", action.get("action_id")
            )
            raise ActionBlock(action.get("action_id"))
        elif action.get("status") == ACTIONS["ACTION_REDIRECT"]:
            LOGGER.debug(
                "Action %s redirected the request to %r",
                action.get("action_id"),
                action["target_url"],
            )
            raise ActionRedirect(action.get("action_id"), action["target_url"])
        elif action.get("status") == ACTIONS["OVERRIDE"]:
            return action.get("new_return_value")
        elif action.get("status") == ACTIONS["MODIFY_ARGS"]:
            if valid_args(action["args"]):
                args, kwargs = action["args"]

        # Call original method
        retry = True
        while retry is True:
            try:
                retry = False
                # Try to call original function
                result = wrapped(*args, **kwargs)
            except Exception:
                # In case of error, call fail callbacks with exception infos
                exc_info = sys.exc_info()

                # Either raise an exception, set a return value or retry
                action = execute_failing_callbacks(
                    key, strategy, instance, exc_info, args, kwargs,
                    storage=storage
                )

                if action.get("status") == ACTIONS["RAISE"]:
                    LOGGER.debug(
                        "Callback %s detected an attack",
                        action.get("rule_name"),
                    )
                    raise AttackBlocked(action.get("rule_name"))
                elif action.get("status") == ACTIONS["RETRY"]:
                    retry = True
                elif action.get("status") == ACTIONS["OVERRIDE"]:
                    return action.get("new_return_value")

                # Be sure to raise if no retry or override
                if retry is False:
                    raise

        # Then call post callback in reverse order to simulate decorator
        # behavior
        action = execute_post_callbacks(
            key, strategy, instance, result, args, kwargs, storage=storage,
        )

        if action.get("status") == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )
            raise AttackBlocked(action.get("rule_name"))
        elif action.get("status") == ACTIONS["OVERRIDE"]:
            return action.get("new_return_value")

        # And return the original value
        return result
    return wrapper


def hook_point(strategy, hook_name, hook_method, original, storage=runtime):
    wrapper = hook_point_wrapper(strategy, hook_name, hook_method, storage)
    return FunctionWrapper(original, wrapper)
