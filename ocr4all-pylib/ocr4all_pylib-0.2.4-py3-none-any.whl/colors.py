from __future__ import annotations

import itertools
import json
import multiprocessing
import os
import random
from ast import literal_eval
from typing import Tuple, Dict, Union, Iterable, Optional, List

import numpy as np
from PIL import Image

from ocr4all.files import imread
from ocr4all.optional import tqdm

from collections.abc import Sequence

DEFAULT_COLOR_MAPPING = {(255, 255, 255): (0, 'bg'),
                         (255, 0, 0): (1, 'text'),
                         (0, 255, 0): (2, 'image')}

DEFAULT_LABELS_BY_NAME = {str(v[1]): v[0] for v in DEFAULT_COLOR_MAPPING.values()}
DEFAULT_LABEL_NAMES_BY_LABEL = {v: k for k, v in DEFAULT_LABELS_BY_NAME.items()}


class ColorException(Exception):
    pass


class ColorMap:
    """
    Maps between 2D label arrays and RGB images. Supports up to 256 labels.
    """

    label_by_name: Dict[str, int]
    palette: Image.Image
    mapping: Dict[Tuple[int, int, int], Union[int, Tuple[int, str]]]

    _labels: List[int]

    def __init__(self, mapping: Dict[Tuple[int, int, int], Union[int, Tuple[int, str]]]):
        """
        Create an image map from a dictionary. The dict uses RGB triples as keys. The values may be either the label
        values as ints or as a tuple of an int and a string containing a human-readable label.
        :param mapping: mapping from RGB to label. see DEFAULT_IMAGE_MAP for an example
        """
        self.label_by_name = {}
        self._labels = []
        palette_arr = [0] * 768

        def add_label(v: int):
            self._labels.append(v)
            for i in [0, 1, 2]:
                palette_arr[3 * v + i] = k[i]

        for k, v in mapping.items():
            if isinstance(v, Sequence):
                self.label_by_name[v[1]] = v[0]
                add_label(v[0])
            else:
                if DEFAULT_LABEL_NAMES_BY_LABEL.get(v) is not None:
                    self.label_by_name[DEFAULT_LABEL_NAMES_BY_LABEL[v]] = v
                add_label(v)
        self.palette = Image.new("P", (1, 1), None)
        self.palette.putpalette(palette_arr)
        self.mapping = mapping

    def to_labels(self, rgb_image: Union[np.ndarray, Image.Image], strict: bool = False) -> np.ndarray:
        """
        Convert input image to 2D label array.
        :param rgb_image: either 3D numpy array or PIL image
        :param strict: if true, raise an exception if image contains unknown colors, but is slower. otherwise, labels
             for unknown colors are determined by PIL's quantize, which may cause unexpected results.
        """

        if strict:
            for k in get_image_colors(np.asarray(rgb_image)):
                if tuple(k) not in self.mapping.keys():
                    raise ColorException(
                        f"strict mode: image contains unmapped rgb color: {tuple(k)}\nKnown colors: {self.mapping.keys()}")

        if type(rgb_image) is np.ndarray:
            rgb_image = Image.fromarray(rgb_image)

        return np.asarray(rgb_image.quantize(palette=self.palette))

    def to_image(self, labels: np.ndarray, strict: bool = False) -> Image.Image:
        """
        Convert input image to an RGB image
        :param labels: 2D numpy array
        :param strict: if true, raise an exception if input contains unknown labels, but is slower. otherwise, unknown
            labels are mapped to black
        """
        if strict:
            for k in np.unique(labels):
                if k not in self._labels:
                    raise ColorException(f"strict mode: unmapped label: {k}")
        out = Image.fromarray(labels.astype(np.uint8), mode='P')
        out.putpalette(self.palette.getpalette())
        return out.convert('RGB')

    def to_rgb_array(self, labels: np.ndarray, strict: bool = False) -> np.ndarray:
        return np.asarray(self.to_image(labels, strict))

    def imread_labels(self, path: str) -> np.ndarray:
        pil_image = Image.open(path)
        if pil_image.mode not in ('RGB', 'L'):
            pil_image = pil_image.convert('RGB')
        return self.to_labels(pil_image)

    def color_for_label(self, label: Union[str, int]) -> Optional[Tuple[int, int, int]]:
        if type(label) is str:
            label = self.label_by_name.get(label)
            if label is None: return None
        for k, v in self.mapping.items():
            if isinstance(v, Sequence):
                v = v[0]
            if v == label:
                return k
        return None

    def filter_label(self, image: Union[np.ndarray, Image.Image], label: Union[int, str]) -> np.ndarray:
        """
        Find pixels with a specific label
        :param image: label array, RGB array, or PIL Image.
        :param label: either as int or name
        :return: 2D boolean array, true where the pixel matched the label
        """
        if type(image) is Image.Image or len(image.shape) > 2:
            image = self.to_labels(image)
        if type(label) is str:
            label = self.label_by_name[label]
        return image == label

    @staticmethod
    def load(path: str) -> ColorMap:
        """
        Load a ColorMap from a json file. The JSON file must contain an object with the RGB tuples as keys
        (a string of the form "(r, g, b)", where r, g and b are ints) and either an int or an array consisting of an int
        and a string as values (see __init__).
        :param path: path to the json file
        :return: a parsed ColorMap
        """
        if not os.path.exists(path):
            raise Exception("Cannot open {}".format(path))

        with open(path) as f:
            data = json.load(f)
        color_map = {literal_eval(k): v for k, v in data.items()}
        return ColorMap(color_map)

    def save(self, path: str) -> None:
        """
        Write to json in the format specified in the load method's documentation.
        :param path: target file location
        """
        with open(path, 'w') as fp:
            json.dump({str(k): v for k, v in self.mapping.items()}, fp)

    def __len__(self):
        return len(self.mapping)


def get_image_colors(mask: np.ndarray) -> Iterable[Tuple[int, int, int]]:
    if mask.ndim == 2 or mask.shape[2] == 2:
        return [(255, 255, 255), (0, 0, 0)]

    return [tuple(n) for n in np.unique(mask.reshape(-1, mask.shape[2]), axis=0)]


def compute_from_images(input_dir: str, output_dir: Optional[str] = None, max_images: Optional[int] = None,
                        processes: int = 4):
    if not os.path.exists(input_dir):
        raise FileNotFoundError("Cannot open {}".format(input_dir))
    files = [f for f in (os.path.join(input_dir, ent) for ent in os.listdir(input_dir)) if os.path.isfile(f)]

    if max_images is not None:
        print("Before:", files)
        files = random.sample(files, max_images)
        print("after:", files)

    with multiprocessing.Pool(processes=processes) as p:
        image_colors = list(
            tqdm(p.imap(get_image_colors, (imread(f) for f in files)), total=len(files)))
    unique_colors = set(itertools.chain.from_iterable(image_colors))
    sorted_colors = sorted(unique_colors, key=lambda element: (element[0], element[1], element[2]))[::-1]
    color_dict = {key: value for (value, key) in enumerate(sorted_colors)}
    if output_dir:
        color_dict_json = {str(key): (value, "label") for key, value in color_dict.items()}
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'color_map.json'), 'w') as fp:
            json.dump(color_dict_json, fp)

    return color_dict
