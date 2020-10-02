# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Classes and functions to inject data for yolo object detection model """

import os
import cv2
import numpy as np
import torch

from azureml.core import Dataset as AmlDataset
from torch.utils.data import Dataset

from azureml.contrib.automl.dnn.vision.object_detection.data.datasets import FileObjectDetectionDatasetWrapper, \
    AmlDatasetObjectDetectionWrapper
from azureml.contrib.automl.dnn.vision.object_detection_yolo.utils.utils import get_image, convert_to_yolo_labels, \
    letterbox
from azureml.contrib.automl.dnn.vision.common.labeled_dataset_helper import AmlLabeledDatasetHelper
from azureml.contrib.automl.dnn.vision.common.logging_utils import get_logger

logger = get_logger(__name__)


def _collate_function(batch):
    """Custom collate function for training and validation

    :param batch: list of samples (image, label and path)
    :type batch: list
    :return: Images, Labels and Image Paths
    :rtype: tuple of (image pixels), tuple of (bbox information), tuple of (image path)
    """
    img, label, path = zip(*batch)  # transposed
    for i, l in enumerate(label):
        l[:, 0] = i  # add target image index for build_targets()
    return torch.stack(img, 0), torch.cat(label, 0), path


class FileObjectDetectionDatasetWrapperYolo(FileObjectDetectionDatasetWrapper):
    """Wrapper for object detection dataset for Yolo"""

    def __init__(self, annotations_file=None, image_folder=".", is_train=False,
                 prob=0.5, ignore_data_errors=True,
                 use_bg_label=False, label_compute_func=convert_to_yolo_labels,
                 settings=None):
        """TODO RK: comments"""

        # TODO RK: find a better way to pass the settings - assuming some properties in the dict is not good design
        self._img_size = settings['img_size']
        super(FileObjectDetectionDatasetWrapperYolo, self).__init__(
            annotations_file=annotations_file, image_folder=image_folder, is_train=is_train,
            prob=prob, ignore_data_errors=ignore_data_errors, use_bg_label=use_bg_label,
            label_compute_func=label_compute_func, settings=settings)

    @property
    def img_size(self):
        """Image size.

        :return: Image size
        :rtype: int
        """
        return self._img_size

    def __getitem__(self, index):
        """TODO RK: bad design to assume the fields in the parent - rely on properties"""
        return get_image(index, self._image_urls, self._img_size,
                         self._labels, self._settings, self._is_train)

    def collate_function(self, batch):
        """Collate function to use to form a batch"""
        return _collate_function(batch)


class AmlDatasetObjectDetectionWrapperYolo(AmlDatasetObjectDetectionWrapper):
    """Wrapper for Aml labeled dataset for object detection dataset"""

    def __init__(self, dataset_id, is_train=False, settings=None,
                 workspace=None, ignore_data_errors=False,
                 datasetclass=AmlDataset, download_files=True):
        """
        :param dataset_id: dataset id
        :type dataset_id: str
        :param is_train: which mode (training, inferencing) is the network in?
        :type is_train: boolean
        :param settings: yolo specific settings
        :type settings: dict
        :param ignore_data_errors: Setting this ignores and files in the labeled dataset that fail to download.
        :type ignore_data_errors: bool
        :param datasetclass: The source dataset class.
        :type datasetclass: class
        :param download_files: Flag to download files or not.
        :type download_files: bool
        """
        self._img_size = settings['img_size']
        super().__init__(dataset_id=dataset_id, is_train=is_train,
                         workspace=workspace, ignore_data_errors=ignore_data_errors,
                         datasetclass=datasetclass, download_files=download_files,
                         use_bg_label=False, label_compute_func=convert_to_yolo_labels,
                         settings=settings)

    @property
    def img_size(self):
        """Image size.

        :return: Image size
        :rtype: int
        """
        return self._img_size

    def __getitem__(self, index):
        """TODO RK: bad design to assume the fields in the parent - rely on properties"""
        return get_image(index, self._image_urls, self._img_size,
                         self._labels, self._settings, self._is_train)

    def collate_function(self, batch):
        """Collate function to use to form a batch"""
        return _collate_function(batch)


class PredictionDataset_yolo(Dataset):
    """Dataset file so that score.py can process images in batches.

    """

    def __init__(self, root_dir=None, image_list_file=None, ignore_data_errors=True,
                 input_dataset_id=None, ws=None, datasetclass=AmlDataset):
        """
        :param root_dir: prefix to be added to the paths contained in image_list_file
        :type root_dir: str
        :param image_list_file: path to file containing list of images
        :type image_list_file: str
        :param ignore_data_errors: boolean flag on whether to ignore input data errors
        :type ignore_data_errors: bool
        :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
        :type input_dataset_id: str
        :param ws: The Azure ML Workspace
        :type ws: Workspace
        :param datasetclass: The Azure ML Datset class
        :type datasetclass: Dataset

        """
        self._files = []

        if input_dataset_id is not None:
            dataset_helper = AmlLabeledDatasetHelper(input_dataset_id, ws, ignore_data_errors,
                                                     image_column_name=AmlLabeledDatasetHelper.PATH_COLUMN_NAME,
                                                     datasetclass=datasetclass)
            self._files = dataset_helper.get_file_name_list()
            self._files = [f.strip("/") for f in self._files]
            self._root_dir = dataset_helper._data_dir
        else:
            for filename in open(image_list_file):
                self._files.append(filename.strip())

            # Size of image list file before removing blank strings
            logger.info('Image list file contains {} lines before removing blank '
                        'strings'.format(len(self._files)))

            # Remove blank strings
            self._files = [f for f in self._files if f]
            self._root_dir = root_dir

        # Length of final dataset
        logger.info('Size of dataset: {}'.format(len(self._files)))
        self._ignore_data_errors = ignore_data_errors

    def __len__(self):
        """Size of the dataset."""
        return len(self._files)

    def __getitem__(self, idx):
        """
        :param idx: index
        :type idx: int
        :return: item and label at index idx
        :rtype: tuple[str, image]
        """
        filename = self._files[idx]
        if self._root_dir and filename:
            filename = filename.lstrip('/')
        full_path = os.path.join(self._root_dir, filename)

        _, image, pad = self._read_image(full_path)
        return filename, image, pad

    # TODO RK: use the same reading method as OD
    def _read_image(self, image_url, img_size=640):
        img0 = cv2.imread(image_url)  # BGR
        assert img0 is not None, 'Image Not Found ' + image_url

        img, ratio, pad = letterbox(img0, new_shape=img_size, auto=False, scaleup=False)

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x640x640
        img = np.ascontiguousarray(img)
        return image_url, torch.from_numpy(img), pad

    @staticmethod
    def collate_fn(batch):
        """Custom collate function for inference

        :param batch: list of samples (path, image and pad)
        :type batch: list
        :return: Paths, Images and Pads
        :rtype: tuple of (image path), tuple of (image pixels), tuple of (pad used in letterbox image)
        """
        fname, imgs, pad = zip(*batch)
        return fname, torch.stack(imgs, 0), pad
