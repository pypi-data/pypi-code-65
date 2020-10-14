from typing import *

import magic

from secure_file_detection import constants, validators
from secure_file_detection.exceptions import *
from secure_file_detection.typing_types import *
from secure_file_detection.utils import *

__all__ = [
    "detect_true_type", "is_file_manipulated"
]

CUSTOM_FUNC_MAP = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",  # .docx
    "application/msword": "word",  # .doc
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "powerpoint",  # .pptx
    "application/vnd.ms-powerpoint": "powerpoint",  # .ppt
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",  # .xlsx
    "application/vnd.ms-excel": "excel",  # .xls
}


def get_validator_func(mimetype: str) -> Callable:
    if mimetype in CUSTOM_FUNC_MAP:
        func_name = CUSTOM_FUNC_MAP[mimetype]
    else:
        func_name = "check_" + get_func_name(mimetype)
    
    return getattr(validators, func_name)


def detect_true_type(file: PathLike, *args, **kwargs) -> str:
    """
    Detects the true type of a `file` and returns it's mimetype.
    
    :raises:
        ManipulatedFileError:
            If `raise_if_manipulated` is `True` and the file is manipulated
        MimeTypeNotDetectableError:
            If the mimetype couldn't be checked.
    """
    # Values
    file = get_path(file)
    
    # Preparation
    f = magic.Magic(mime=True)
    
    # Action
    mimetype = f.from_file(str(file))
    
    if mimetype == constants.NOT_DETECTABLE_MIMETYPE:
        raise MimeTypeNotDetectable(f'The mimetype "{mimetype}" is not detectable or the file is manipulated.')

    if mimetype not in constants.SUPPORTED_MIMETYPES:
        raise MimeTypeNotSupported(
            f'The mimetype "{mimetype}" is not supported. You are welcome to make a pull request :)'
        )
    
    # Individual checking
    get_validator_func(mimetype)(file, *args, **kwargs)
    
    # Return mimetype, it is correct
    return mimetype
    

def is_file_manipulated(file: PathLike) -> bool:
    try:
        detect_true_type(file)
    except ManipulatedFileError:
        return True
    return False
    
    
    



