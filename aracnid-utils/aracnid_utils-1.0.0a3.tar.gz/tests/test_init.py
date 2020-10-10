"""Test functions for Aracnid Logger import.
"""
import aracnid_utils

def test_version():
    """Tests that Aracnid Logger was imported successfully.
    """
    assert aracnid_utils.__version__
