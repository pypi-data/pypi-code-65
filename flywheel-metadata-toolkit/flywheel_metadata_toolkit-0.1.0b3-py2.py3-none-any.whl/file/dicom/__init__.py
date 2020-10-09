"""Dicom metadata module"""

import inspect
import logging

import pydicom

from flywheel_metadata.file.dicom.fixer import fw_pydicom_config

log = logging.getLogger(__name__)


def load_dicom(*args, decode=True, config=None, **kwargs):
    """
    Load and optionaly decode dicom dataset with Flywheel pydicom configuration.

    Args:
        *args: pydicom.dcmread args
        decode (bool): decode the dataset if True (default=True)
        config (dict): the kwargs to be passed to the fw_pydicom_config manager (default=None)
        **kwargs: pydicom.dcmread kwargs and fw_pydicom_config kwargs

    Returns:
        pydicom.Dataset
    """
    if not config:
        config = {}

    with fw_pydicom_config(**config):
        dicom_ds = pydicom.dcmread(*args, **kwargs)
        if decode:
            dicom_ds.decode()

    return dicom_ds
