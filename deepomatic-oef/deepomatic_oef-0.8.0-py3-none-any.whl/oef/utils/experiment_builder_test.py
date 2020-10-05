import pytest

from deepomatic.oef.utils.experiment_builder import ExperimentBuilder, InvalidNet
from deepomatic.oef.protos.optimizer_pb2 import LearningRatePolicy, ConstantLearningRate
from deepomatic.oef.protos.models.image.utils.hyperparameters_pb2 import Hyperparams
from deepomatic.oef.configs import model_list
from deepomatic.oef.platform.experiment_to_display_name import experiment_to_display_name


FAKE_DATASET = {'root': 'gs://my/bucket', 'config_path': 'config.prototxt'}


def test_new_model_key():
    # Try should not raise an exception
    ExperimentBuilder("image_detection.pretraining_natural_rgb.faster_rcnn.resnet_50_v1")

def test_old_model_key():
    # Try should not raise an exception
    ExperimentBuilder("image_detection.faster_rcnn.resnet_50_v1.pretraining_natural_rgb")

def test_bad_model_key():
    with pytest.raises(InvalidNet):
        ExperimentBuilder("image_detection.foo.resnet_50_v1.pretraining_natural_rgb")

def test_passing_arg():
    # Try should not raise an exception
    builder = ExperimentBuilder("image_detection.pretraining_natural_rgb.faster_rcnn.resnet_50_v1")
    xp = builder.build(dataset=FAKE_DATASET, batch_size=1000)
    assert xp.trainer.batch_size == 1000

# Do not rename this test: it is used in the Mafile in `make models`
@pytest.mark.parametrize(
    'model_key', list(model_list.model_list.keys())
)
def test_builder(model_key):
    display_name = model_list.model_list[model_key].display_name
    # Test that the builder works for the given model key
    builder = ExperimentBuilder(model_key)
    xp = builder.build(dataset=FAKE_DATASET, exclusive_labels=True)
    # Test that the inferred experiment name matches the declared name
    assert experiment_to_display_name(xp) == display_name

def test_duplicated_oneof_value():
    builder = ExperimentBuilder("image_detection.pretraining_natural_rgb.faster_rcnn.resnet_50_v1")
    with pytest.raises(AssertionError) as excinfo:
        builder.build(dataset=FAKE_DATASET, batch_size=1000, optimizer={'rms_prop_optimizer': {}, 'momentum_optimizer': {}})
    assert "Two values are given for the one-of" in str(excinfo.value)

def test_builder_with_protobuf():
    builder = ExperimentBuilder('image_classification.pretraining_natural_rgb.softmax.inception_v3')
    builder.build(
        learning_rate_policy=LearningRatePolicy(constant_learning_rate=ConstantLearningRate()),
    )

def test_isinstance():
    builder = ExperimentBuilder('image_detection.pretraining_natural_rgb.ssd.inception_v2')
    xp = builder.build()
    value = xp.trainer.image_detection.backbone.hyperparameters
    assert isinstance(value, Hyperparams), 'Expecting {}, got: {}'.format(Hyperparams, value.__class__)
