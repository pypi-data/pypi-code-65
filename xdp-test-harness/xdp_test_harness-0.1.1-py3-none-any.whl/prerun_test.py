from xdp_test_harness.xdp_case import XDPCase

try:
    import scapy
    import bcc
    import hello
except ImportError:
    raise unittest.SkipTest(
        "Such-and-such failed. Skipping all tests in foo.py")
