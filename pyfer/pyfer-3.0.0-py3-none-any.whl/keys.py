"""
PYFER - Encrypt and Decrypt messages.
-------------------------------------
KEYS module: 

Functions
---------
generate_key: creates a random string of digits.
"""

import numpy as np

# ------------------------------------------------------------------------


def generate_key(key_length):

    """
    Generates a random string of digits of the specified length.
    """

    if type(key_length) is int:
        n = key_length
    else:
        raise Exception(
            f"key_length argument must be an integer; {type(key_length)} given."
        )

    str_key = "".join(
        ["{}".format(np.random.randint(10)) for num in range(0, n)]
    )

    return str_key
