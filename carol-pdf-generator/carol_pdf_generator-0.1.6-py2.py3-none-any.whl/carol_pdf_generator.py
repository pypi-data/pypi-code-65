import hashlib
from io import BytesIO
from urllib import request

from datauri import DataURI
from fpdf import FPDF


def get_image_data(base64_data_uri: str) -> BytesIO:
    """Get the image data from a base64 data uri

    Args:
        base64_data_uri (str): Base64 encoded image

    Returns:
        bytes: decoded image
    """

    return BytesIO(request.urlopen(base64_data_uri).read())


def image_supported(base64_data: str) -> bool:
    """Check if the image is supported by this lib

    Args:
        base64_data (str): base64 data uri image

    Returns:
        bool: true if base64 data type is jpeg or png
    """
    return get_image_type(base64_data) in ['png', 'jpeg', 'jpg']


def get_image_type(base64_data: str) -> bool:
    """Returns the image file type

    Args:
        base64_data (str): base64 data uri image

    Returns:
        bool: true if base64 data type is jpeg or png
    """
    uri = DataURI(base64_data)
    return uri.mimetype.replace('image/', '')


def get_from_base64_list(image_list: list, output_file: str = None) -> str:
    """Creates PDF from a list of base64 images

    Args:
        image_list (list): List of base64 images data:image/[jpeg|png]
        output_file (str, optional): Path of output PDF. Defaults to None.

    Returns:
        str: data uri with base64 PDF file
    """

    pdf = FPDF()
    pdf.set_compression(True)

    for image in image_list:
        if image_supported(image):
            result = hashlib.md5(image.encode())
            filename = f'{result.hexdigest()}.{get_image_type(image)}'
            pdf.add_page()
            pdf.image(
                name=filename,
                x=0,
                y=0,
                w=210,
                image_fp=get_image_data(image)
            )

    if output_file is not None:
        pdf.output(output_file, 'F')

    pdf_data = pdf.output(dest='S')

    data_uri = DataURI.make(
        mimetype='application/pdf',
        charset='latin1',
        base64=True,
        data=pdf_data
    )
    return data_uri


def get_from_file_list(images: list, output_file: str = None) -> str:
    """Creates PDF from a list of images paths

    Args:
        image_list (list): List of images paths
        output_file (str, optional): Path of output PDF. Defaults to None.

    Returns:
        str: data uri with base64 PDF file
    """
    data_uri_list = []

    for image_path in images:
        data_uri = DataURI.from_file(image_path)
        if image_supported(data_uri):
            data_uri_list.append(data_uri)

    return get_from_base64_list(data_uri_list, output_file=output_file)
