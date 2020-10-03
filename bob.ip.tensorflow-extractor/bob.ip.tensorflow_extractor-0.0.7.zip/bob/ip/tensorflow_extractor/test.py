import bob.io.base
import bob.io.image
from bob.io.base.test_utils import datafile
import numpy
import json

numpy.random.seed(10)


def test_facenet():
    from bob.ip.tensorflow_extractor import FaceNet

    extractor = FaceNet()
    data = numpy.random.rand(3, 160, 160).astype("uint8")
    output = extractor(data)
    assert output.size == 128, output.shape


def test_mtcnn():
    test_image = datafile("mtcnn/test_image.png", __name__)
    ref_numbers = datafile("mtcnn/mtcnn.hdf5", __name__)
    ref_annots = datafile("mtcnn/mtcnn.json", __name__)
    from bob.ip.tensorflow_extractor import MTCNN

    mtcnn = MTCNN()
    img = bob.io.base.load(test_image)
    bbox, prob, landmarks = mtcnn.detect(img)
    with bob.io.base.HDF5File(ref_numbers, "r") as f:
        ref_bbox = f["bbox"]
        ref_scores = f["scores"]
        ref_landmarks = f["landmarks"]

    assert numpy.allclose(bbox, ref_bbox), (bbox, ref_bbox)
    assert numpy.allclose(prob, ref_scores), (prob, ref_scores)
    assert numpy.allclose(landmarks, ref_landmarks), (landmarks, ref_landmarks)

    annots = mtcnn.annotations(img)
    ref_annots = json.load(open(ref_annots))
    assert len(annots) == len(ref_annots), (len(annots), len(ref_annots))
    for a, aref in zip(annots, ref_annots):
        for k, v in a.items():
            vref = aref[k]
            assert numpy.allclose(v, vref)
