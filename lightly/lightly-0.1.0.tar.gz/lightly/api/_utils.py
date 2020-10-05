""" Communication Utility """

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import io
import os

import numpy as np
import warnings
from PIL import Image, ImageFilter

# the following two lines are needed because
# PIL misidentifies certain jpeg images as MPOs
from PIL import JpegImagePlugin
JpegImagePlugin._getmp = lambda: None

LEGAL_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']
MAXIMUM_FILENAME_LENGTH = 80
MAX_WIDTH, MAX_HEIGHT = 2048, 2048


def getenv(key, default):
    """Return the value of the environment variable key if it exists,
       or default if it doesn’t.

    """
    try:
        return os.getenvb(key.encode(), default.encode()).decode()
    except Exception:
        pass
    try:
        return os.getenv(key, default)
    except Exception:
        pass
    return default


def PIL_to_bytes(img, ext='png', quality=None):
    """Return the PIL image as byte stream. Useful to send image via requests.

    """
    bytes_io = io.BytesIO()
    if quality is not None:
        img.save(bytes_io, format=ext, quality=quality)
    else:
        subsampling = -1 if ext.lower() in ['jpg', 'jpeg'] else 0
        img.save(bytes_io, format=ext, quality=100, subsampling=subsampling)
    bytes_io.seek(0)
    return bytes_io


def image_mean(np_img):
    """Return mean of each channel

    """
    return np_img.mean(axis=(0, 1))


def image_std(np_img):
    """Return standard deviation of each channel

    """
    return np_img.std(axis=(0, 1))


def sum_of_values(np_img):
    """Return the sum of the pixel values of each channel

    """
    return np_img.sum(axis=(0, 1))


def sum_of_squares(np_img):
    """Return the sum of the squared pixel values of each channel

    """
    return (np_img ** 2).sum(axis=(0, 1))


def signal_to_noise_ratio(img, axis=None, ddof=0):
    """Calculate the signal to noise ratio of the image

    """
    np_img = np.asanyarray(img)
    mean = np_img.mean(axis=axis)
    std = np_img.std(axis=axis, ddof=ddof)
    return np.where(std == 0, 0, mean / std)


def sharpness(img):
    """Calculate the sharpness of the image using a Laplacian Kernel

    """
    img_bw = img.convert('L')
    filtered = img_bw.filter(
        ImageFilter.Kernel(
            (3, 3),
            # Laplacian Kernel:
            (-1, -1, -1, -1, 8, -1, -1, -1, -1),
            1,
            0,
        )
    )
    return np.std(filtered)


def size_in_bytes(img):
    """Return the size of the image in bytes

    """
    img_file = io.BytesIO()
    img.save(img_file, format=img.format)
    return img_file.tell()


def shape(np_img):
    """Shape of the image as np.ndarray

    """
    return np_img.shape


def get_meta_from_img(img):
    """Calculate the following metadata from a PIL image:
       - Mean
       - Standard Deviation
       - Signal To Noise
       - Sharpness
       - Size in Bytes
       - Shape
       - Sum of Values
       - Sum of Squares

    Args:
        img: (PIL Image)

    Returns:
        A dictionary containing the metadata of the image.
    """

    np_img = np.array(img) / 255.0
    metadata = {
        'mean': image_mean(np_img).tolist(),
        'std': image_std(np_img).tolist(),
        'snr': float(signal_to_noise_ratio(img)),
        'sharpness': float(sharpness(img)),
        'sizeInBytes': size_in_bytes(img),
        'shape': list(shape(np_img)),
        'sumOfValues': sum_of_values(np_img).tolist(),
        'sumOfSquares': sum_of_squares(np_img).tolist(),
    }
    return metadata


def get_thumbnail_from_img(img, size=80):
    """Compute the thumbnail of the image

    Args:
        img: (PIL Image)

    Returns:
        Thumbnail as PIL Image

    """
    thumbnail = img.copy()
    thumbnail.thumbnail((size, size), Image.LINEAR)
    return thumbnail


def resize_image(image, max_width, max_height):
    """

    """
    width = image.width
    height = image.height
    new_image = image.copy()
    new_image.format = image.format

    width_factor = max_width / width
    height_factor = max_height / height
    factor = min(width_factor, height_factor)
    new_image.resize(
        (
            np.floor(factor * width).astype(int),
            np.floor(factor * height).astype(int)
        )
    )
    return new_image


def check_image(filename):
    """Checks whether an image is corrupted or not,
       calculates metadata, and opens file handles for
       image and thumbnail if requested

    Args:
        filename: (str) Path to the file

    Returns:
        A dictionary of metadata and a flag whether file is corrupted
    """

    basename = os.path.basename(filename)
    if len(basename) > MAXIMUM_FILENAME_LENGTH:
        msg = f'Filename {basename} is longer than the allowed maximum of'
        msg += f'{MAXIMUM_FILENAME_LENGTH} character and will be skipped.'
        warnings.warn(msg)
        return None, None, {}, True

    is_corrupted = False
    corruption = ''
    image = Image.open(filename)
    try:
        image.load()
    except IOError as e:
        is_corrupted = True
        corruption = e
    if not is_corrupted and image.format.lower() not in LEGAL_IMAGE_FORMATS:
        is_corrupted = True
        corruption = f'Illegal image format {image.format}.'
    image.close()

    if is_corrupted:
        metadata = {
            'corruption': corruption
        }
    else:
        image = Image.open(filename, 'r')
        metadata = get_meta_from_img(image)
        metadata['corruption'] = ''
        image.close()
    metadata['is_corrupted'] = is_corrupted

    return metadata, is_corrupted
