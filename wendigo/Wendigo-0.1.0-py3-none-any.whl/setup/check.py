import ctypes
import os
import struct
import warnings
from wendigo.exceptions import PlatformNotSupportException
from wendigo.warnings import AdministrationWarning

__all__ = ["IS_ADMIN"]

def check_os():
    """
    Chack if the OS is supported or not.
    """
    if os.name != "nt":
        raise PlatformNotSupportException("Wendigo is only for Windows.")

    python_bit = struct.calcsize("P") * 8
    if python_bit != 64:
        raise PlatformNotSupportException("Wendigo is available only in 64 bit mode.")

check_os()

def check_admin():
    """
    Check if it's running as an administrator or not.
    """
    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except:
        is_admin = False

    if not is_admin:
        warnings.warn("Run as an administrator, or some functions won't work.", AdministrationWarning)
    
    return is_admin

IS_ADMIN = check_admin()