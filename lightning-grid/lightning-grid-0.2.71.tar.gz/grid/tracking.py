"""
Tracking module for Grid. Here we include logic
for tracking how users interact with the backend,
which helps us have a better picture of what the
complete user journey is across our product.

All of our tracking is done via the use of Segment
events. [1]

References
----------
[1] https://segment.com/docs/sources/server/python/
"""
import os
import analytics
import datetime
import grid.globals as env

from typing import Optional


class Segment:
    """Class for sending data to Grid's Segment analytics tracker."""
    def __init__(self):
        analytics.write_key = env.SEGMENT_KEY
        analytics.debug = not bool(os.getenv('SEGMENT_TRACKING'))
        analytics.on_error = self.handle_error

    @staticmethod
    def handle_error(error, items):  # pragma: no cover
        if env.DEBUG:
            env.logger.debug(f'Segment error detected: {error}')

    def send(self, event: str, user_id: str, properties: Optional[dict]):
        """Sends a given message to Segment to be recorded"""
        analytics.track(user_id=user_id,
                        event=event,
                        properties=properties,
                        timestamp=datetime.datetime.now())
