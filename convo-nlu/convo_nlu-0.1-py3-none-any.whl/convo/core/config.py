import os
import typing
from typing import Optional, Text, List, Dict, Union

import convo.utils.io

if typing.TYPE_CHECKING:
    from convo.core.policies.policy import Policy


def load(config_file: Optional[Union[Text, Dict]]) -> List["Policy"]:
    """Load policy data stored in the specified file."""
    from convo.core.policies.ensemble import PolicyEnsemble

    if not config_file:
        raise ValueError(
            "You have to provide a valid path to a config file. "
            "The file '{}' could not be found."
            "".format(os.path.abspath(config_file))
        )

    config_data = {}
    if isinstance(config_file, str) and os.path.isfile(config_file):
        config_data = convo.utils.io.read_config_file(config_file)
    elif isinstance(config_file, Dict):
        config_data = config_file

    return PolicyEnsemble.from_dict(config_data)
