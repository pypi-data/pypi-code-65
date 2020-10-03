"""Property binding."""

import logging
from typing import NamedTuple, TYPE_CHECKING, Optional

from aio_wx_widgets.core.validators import ValidationError

if TYPE_CHECKING:
    from aio_wx_widgets.controller import BaseController

_LOGGER = logging.getLogger(__name__)

WATCHERS = "_watchers_"


class Binding(NamedTuple):
    """Binding data."""

    bound_object: "BaseController"
    bound_property: "str"


class Bindable:
    """Base class for binding a property to a widget.

    Make a widget inherit from this. The binding property modifies the controller bound
    property adding a watcher and emitting change events.
    """

    def __init__(self, binding: Optional["Binding"]):
        self._binding = binding

        # Flag to stop firing updates when a property value has changed.
        # Prevents infinite loop of updating the value and firing update events.
        self._fire_update_event = True

    def _make_binding(self):
        if self._binding is None:
            _LOGGER.debug("No binding defined.")
            return

        if WATCHERS not in self._binding.bound_object.__dict__:
            self._binding.bound_object.__dict__[WATCHERS] = {}
        if (
            self._binding.bound_property
            not in self._binding.bound_object.__dict__[WATCHERS]
        ):
            _LOGGER.debug("No watchers yet for %s", self._binding.bound_property)
            self._binding.bound_object.__dict__[WATCHERS][
                self._binding.bound_property
            ] = []
        self._binding.bound_object.__dict__[WATCHERS][
            self._binding.bound_property
        ].append(self._update)

        value = self.get_property_value()

        self._fire_update_event = False
        self._set_ui_value(value)

    def get_property_value(self):
        """Return the property value of the bound object.

        This would be the attribute defined in the controller.
        """
        return getattr(self._binding.bound_object, self._binding.bound_property)

    def _set_property_value(self, value):
        setattr(self._binding.bound_object, self._binding.bound_property, value)

    def _update(self, value):
        """Called when a property changes from outside this control.

        Update the control with the new value
        """
        _LOGGER.debug("Updating entry with new value.")
        self._fire_update_event = False
        self._set_ui_value(value)
        _LOGGER.debug("Updated.")

    def _on_ui_change(self, *args, **kwargs):
        """Callback when UI widget value changes by user input."""
        if self._binding is None:
            return
        _LOGGER.debug("UI value changed on id %s", id(self))
        if not self._fire_update_event:
            _LOGGER.debug("Not updating bindings as fire_update_event is False")
            self._fire_update_event = True
            return
        _LOGGER.debug("Trigger the binding")

        self._update_binding()

        _LOGGER.debug("Firing update")

    def _update_binding(self, force=False):
        """Update the binding property.

        Args:
            force: [bool] this will force the value to be cast into the value according
                to the validator.

        """
        try:
            val = self._get_ui_value(force)
        except ValidationError as err:
            self.display_error(err)
        else:
            self._set_property_value(val)
            self._fire_update_event = True

    def display_error(self, exception: ValidationError):
        """To be overridden by the parent class.

        Use this to display the error info on the widget.
        """

    def _get_ui_value(self, force: bool):
        """Get the value from the ui widget.

        Raises pydantic.ValidationError when validation fails.
        """
        raise NotImplementedError()

    def _set_ui_value(self, value):
        raise NotImplementedError()
