"""

This file contains the sensor class for the youless API

"""


class YoulessSensor:
    """A wrapper class to contain the Youless Sensor values."""

    def __init__(self, value, uom):
        """Initialize the value wrapper."""
        self._value = value
        self._uom = uom

    @property
    def unit_of_measurement(self):
        """Get the unit of measurement for this value."""
        return self._uom

    @property
    def value(self):
        """Get the current value"""
        return self._value
