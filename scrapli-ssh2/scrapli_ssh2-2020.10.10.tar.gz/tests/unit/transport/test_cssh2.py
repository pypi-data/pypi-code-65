import sys

import pytest

from scrapli_ssh2.transport import Transport


@pytest.mark.skipif(
    (sys.platform.startswith("win") and sys.version_info > (3, 7)),
    reason="ssh2 on pypi not built for python3.8 on windows",
)
def test_creation():
    conn = Transport("localhost")
    assert conn.host == "localhost"
    assert conn.port == 22
