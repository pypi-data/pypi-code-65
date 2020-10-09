__all__ = [
    "RecordMixin",
    "ImageidRecordMixin",
    "FilepathRecordMixin",
    "SizeRecordMixin",
    "LabelsRecordMixin",
    "BBoxesRecordMixin",
]
from icevision.imports import *
from .bbox import *


class RecordMixin:
    # TODO: as_dict is only necessary because of backwards compatibility
    def as_dict(self) -> dict:
        return {}


class RecordMetadataMixin:
    pass


class RecordAnnotationMixin:
    pass


class ImageidRecordMixin(RecordMixin):
    def set_imageid(self, imageid: int):
        self.imageid = imageid

    def as_dict(self) -> dict:
        return {"imageid": self.imageid, **super().as_dict()}


class FilepathRecordMixin(RecordMixin):
    def set_filepath(self, filepath: Path):
        self.filepath = filepath

    def as_dict(self) -> dict:
        return {"filepath": self.filepath, **super().as_dict()}


class SizeRecordMixin(RecordMixin):
    def set_image_size(self, width: int, height: int):
        self.width, self.height = width, height

    def as_dict(self) -> dict:
        return {"width": self.width, "height": self.height, **super().as_dict()}


### Annotation parsers ###
class LabelsRecordMixin(RecordMixin):
    def __init__(self):
        super().__init__()
        self.labels: List[int] = []

    def is_valid(self) -> List[bool]:
        return [True for _ in self.labels]

    def add_labels(self, labels: List[int]):
        self.labels.extend(labels)

    def as_dict(self) -> dict:
        return {"labels": self.labels, **super().as_dict()}


class BBoxesRecordMixin:
    def __init__(self):
        super().__init__()
        self.bboxes: List[BBox] = []

    def is_valid(self) -> List[bool]:
        super_valids = super().is_valid()
        valids = [bbox.is_valid(self.width, self.height) for bbox in self.bboxes]

        return valids + super_valids

    def add_bboxes(self, bboxes):
        self.bboxes.extend(bboxes)

    def as_dict(self) -> dict:
        return {"bboxes": self.bboxes, **super().as_dict()}
