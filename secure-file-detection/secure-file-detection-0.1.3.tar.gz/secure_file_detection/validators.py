import imghdr
import sndhdr
from collections import namedtuple
from pathlib import Path
from typing import *

import chardet
import vidhdr
from docx import Document
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from pdfminer.high_level import extract_text
from pdfminer.psparser import PSException
from pptx import Presentation
from svglib.svglib import CircularRefError, svg2rlg

from secure_file_detection.exceptions import *
from secure_file_detection.utils import *


def _easy_check(real_type: str, expected_type: str):
    if real_type is None:
        raise ManipulatedFileError(construct_error_message(expected_type, real_type))
    
    image_type = get_type_from_mimetype(expected_type)
    if real_type != image_type:
        raise ManipulatedFileError(construct_error_message(expected_type, real_type))


def _easy_image_check(file: Path, expected_type: str):
    real_type_tuple: namedtuple = imghdr.what(file)

    _easy_check(real_type_tuple, expected_type)


def _easy_audio_check(file: Path, expected_type: str):
    real_type = sndhdr.what(file)
    
    _easy_check(real_type, expected_type)


def _easy_video_check(file: Path, expected_type: str):
    real_type = vidhdr.what(str(file))
    real_type = get_type_from_mimetype(real_type)
    
    _easy_check(real_type, expected_type)


def _easy_text_check(file: Path, allowed_encodings: Optional[Set[str]] = None):
    """Validates the encoding."""
    DEFAULT_ENCODINGS = {
        *(
            f"windows-{number}"
            for number in range(1250, 1255 + 1)
        ),
        "utf-8", "utf-16", "utf-32",
        "ascii"
    }
    
    # Values
    allowed_encodings = allowed_encodings or DEFAULT_ENCODINGS
    
    with file.open("rb") as opened_file:
        data = opened_file.read()
    
    result = chardet.detect(data)
    if result["encoding"].lower() not in allowed_encodings:
        raise ManipulatedFileError("The file has an disallowed encoding type!")


# IMAGE

def check_image_jpeg(file: Path):
    _easy_image_check(file, "image/jpeg")


def check_image_gif(file: Path):
    _easy_image_check(file, "image/gif")


def check_image_tiff(file: Path):
    _easy_image_check(file, "image/tiff")


def check_image_bmp(file: Path):
    _easy_image_check(file, "image/bmp")


def check_image_png(file: Path):
    _easy_image_check(file, "image/png")


def check_image_svg(file: Path):
    try:
        result = svg2rlg(str(file))
    except CircularRefError:
        result = None
    
    if result is None:
        raise ManipulatedFileError(construct_error_message("image/svg"))
        

# AUDIO

def check_audio_aiff(file: Path):
    _easy_audio_check(file, "audio/aiff")


def check_audio_x_voc(file: Path):
    _easy_audio_check(file, "audio/x-voc")


def check_audio_wav(file: Path):
    _easy_audio_check(file, "audio/wav")


# VIDEO


def check_video_mp4(file: Path):
    _easy_video_check(file, "video/mp4")


def check_video_3gpp(file: Path):
    _easy_video_check(file, "video/3gpp")


def check_video_quicktime(file: Path):
    _easy_video_check(file, "video/quicktime")


def check_text_plain(file: Path, *args, **kwargs):
    _easy_text_check(file, *args, **kwargs)


# MICROSOFT

def check_word(file: Path):
    try:
        Document(str(file))
    except ValueError:
        raise ManipulatedFileError(construct_error_message("Word-Document (.docx)"))


def check_powerpoint(file: Path):
    try:
        Presentation(str(file))
    except ValueError:
        raise ManipulatedFileError(construct_error_message("Powerpoint-Show (.pptx)"))


def check_excel(file: Path):
    try:
        load_workbook(str(file))
    except InvalidFileException:
        raise ManipulatedFileError(construct_error_message("Excel-File (.xlsx)"))


def check_application_pdf(file: Path):
    try:
        extract_text(str(file))
    except PSException:
        raise ManipulatedFileError(construct_error_message("application/pdf"))
