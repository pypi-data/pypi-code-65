from __future__ import annotations

import itertools
import json
import multiprocessing
import os
import random
from ast import literal_eval
from typing import Tuple, Dict, Union, Iterable, Optional

import numpy as np
from PIL import Image

from ocr4all.files import imread
from ocr4all.optional import tqdm

DEFAULT_IMAGE_MAP = {(255, 255, 255): [0, 'bg'],
                     (255, 0, 0): [1, 'text'],
                     (0, 255, 0): [2, 'image']}

DEFAULT_REVERSE_IMAGE_MAP = {v[1]: np.array(k) for k, v in DEFAULT_IMAGE_MAP.items()}


class ImageMap:
    def __init__(self, mapping: Dict[Tuple[int, int, int], Union[int, Tuple[int, str]]]):
        """
        Create an image map from a dictionary. The dict uses RGB triples as keys. The values may be either the label
        values as ints or as a tuple of an int and a string containing a human-readable label.
        :param mapping: mapping from RGB to label. see DEFAULT_IMAGE_MAP for an example
        """
        palette_arr = [0] * 768
        for k, v in mapping.items():
            from collections.abc import Sequence
            if isinstance(v, Sequence):
                v = v[0]
            for i in [0, 1, 2]:
                palette_arr[3 * v + i] = k[i]
        self.palette = Image.new("P", (1, 1), None)
        self.palette.putpalette(palette_arr)
        self.mapping = mapping

    def to_labels(self, rgb_image: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """
        Guaranteed to return a 2D int array
        """
        if type(rgb_image) is np.ndarray:
            rgb_image = Image.fromarray(rgb_image)
        return np.asarray(rgb_image.quantize(palette=self.palette))

    def to_image(self, labels: np.ndarray) -> Image.Image:
        out = Image.fromarray(labels, mode='P')
        out.putpalette(self.palette.getpalette())
        return out.convert('RGB')

    def imread_labels(self, path:str) -> np.ndarray:
        pil_image = Image.open(path)
        return self.to_labels(pil_image)

    @staticmethod
    def load(path: str) -> ImageMap:
        """
        Load an ImageMap from a json file. The JSON file must contain an object with the RGB tuples as keys
        (a string of the form "(r, g, b)", where r, g and b are ints) and either an int or an array consisting of an int
        and a string as values (see __init__).
        :param path: path to the json file
        :return: a parsed ImageMap
        """
        if not os.path.exists(path):
            raise Exception("Cannot open {}".format(path))

        with open(path) as f:
            data = json.load(f)
        color_map = {literal_eval(k): v for k, v in data.items()}
        return ImageMap(color_map)

    def save(self, path: str) -> None:
        """
        Write to json in the format specified in the load method's documentation.
        :param path: target file location
        """
        with open(path, 'w') as fp:
            json.dump(self.mapping, fp)


def get_image_colors(mask: np.ndarray) -> Iterable[Tuple[int, int, int]]:
    if mask.ndim == 2 or mask.shape[2] == 2:
        return [(255, 255, 255), (0, 0, 0)]

    return np.unique(mask.reshape(-1, mask.shape[2]), axis=0)


def compute_from_images(input_dir: str, output_dir: str, max_images: Optional[int] = None, processes: int = 4):
    if not os.path.exists(input_dir):
        raise Exception("Cannot open {}".format(input_dir))
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]

    if max_images is not None:
        files = random.sample(files, max_images)

    with multiprocessing.Pool(processes=processes) as p:
        colors = list(tqdm(p.imap(get_image_colors, (imread(f) for f in files)), total=len(files)))
    colors = set(itertools.chain.from_iterable(colors))
    colors = sorted(colors, key=lambda element: (element[0], element[1], element[2]))[::-1]
    color_dict = {str(key): (value, "label") for (value, key) in enumerate(colors)}
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'image_map.json'), 'w') as fp:
        json.dump(color_dict, fp)
