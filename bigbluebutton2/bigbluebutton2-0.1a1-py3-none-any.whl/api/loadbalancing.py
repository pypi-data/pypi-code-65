"""Collection of load balancing checks.

For details on how they are used, see the documentation of
:func:`~bigbluebutton.api.bigbluebuttong.BigBlueButtonGroup.select_api`.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .bigbluebutton import BigBlueButton

CHECKERS: List[Callable[["BigBlueButton", Optional[Dict[str, Any]]], float]] = []
