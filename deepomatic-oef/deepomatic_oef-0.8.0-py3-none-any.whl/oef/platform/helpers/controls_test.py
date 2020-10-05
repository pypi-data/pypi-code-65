import pytest

from deepomatic.oef.protos.experiment_pb2 import Experiment
from deepomatic.oef.protos.trainer_pb2 import Trainer
from deepomatic.oef.protos.models.image.detection_pb2 import Detection

from .common import BadType
from .tags import Tag, Tags
from . import controls


def test_default_for_select():
    # Callable allowed
    controls.SelectControl('foo', 'trainer.model_type', 'bar', [], default_value=lambda x: 1)

    # String allowed
    controls.SelectControl('foo', 'trainer.model_type', 'bar', [], default_value='some.path')

    # Float disallowed
    with pytest.raises(BadType):
        controls.SelectControl('foo', 'trainer.model_type', 'bar', [], default_value=0.5)

    # Bool disallowed
    with pytest.raises(BadType):
        controls.SelectControl('foo', 'trainer.model_type', 'bar', [], default_value=False)

def test_default_for_input():
    # Callable allowed
    controls.InputControl('seed', 'foo', default_value=lambda x: 1)

    # String allowed
    controls.InputControl('seed', 'foo', default_value='some.path')

    # Float allowed
    controls.InputControl('seed', 'foo', default_value=0.5)

    # Bool not allowed
    with pytest.raises(BadType):
        controls.InputControl('seed', 'foo', default_value=False)

def test_default_for_toogle():
    # Callable allowed
    controls.ToggleControl('trainer.use_float16', 'foo', default_value=lambda x: 1)

    # String allowed
    controls.ToggleControl('trainer.use_float16', 'foo', default_value='some.path')

    # Float disallowed
    with pytest.raises(BadType):
        controls.ToggleControl('trainer.use_float16', 'foo', default_value=0.5)

    # Bool not allowed
    controls.ToggleControl('trainer.use_float16', 'foo', default_value=False)


###############################################################################

class FooBar(Tag):
    FOO = 'foo'
    BAR = 'bar'

def test_tags_for_select():
    control = controls.SelectControl('optimizer', 'trainer.optimizer.optimizer', 'message', [
        controls.SelectOption('momentum_optimizer', 'Momentum Optimizer'),
        controls.SelectOption('rms_prop_optimizer', 'RMS Prop Optimizer')
    ], tags={
        'momentum_optimizer': Tags([FooBar.FOO]),
        'rms_prop_optimizer': Tags([FooBar.BAR])
    })

    assert control.value_to_tag_map == {
        'momentum_optimizer': {
            'foobar': 'foo'
        },
        'rms_prop_optimizer': {
            'foobar': 'bar'
        }
    }

def test_select_with_unkown_values():
    with pytest.raises(Exception) as excinfo:
        controls.SelectControl('optimizer', 'trainer.optimizer.optimizer', 'message', [
            controls.SelectOption('foo', 'Momentum Optimizer'),
            controls.SelectOption('bar', 'RMS Prop Optimizer')
        ])
    assert "foo" in str(excinfo.value)
    assert "bar" in str(excinfo.value)


def test_tags_for_toggle():
    control = controls.ToggleControl('trainer.use_float16', 'message', tags=[Tags([FooBar.FOO]), Tags([FooBar.BAR])])

    assert control.value_to_tag_map == {
        False: {
            'foobar': 'foo'
        },
        True: {
            'foobar': 'bar'
        }
    }

def test_get_protobuf_value():
    xp = Experiment(trainer=Trainer(initial_learning_rate=0.12345))
    value = getattr(*controls.protobuf_iterate(xp, 'trainer.initial_learning_rate'))
    assert value == pytest.approx(0.12345)

def test_set_protobuf_value():
    xp = Experiment()
    controls.set_protobuf_value(xp, 0.12345, 'trainer.initial_learning_rate')
    assert xp.trainer.initial_learning_rate == pytest.approx(0.12345)

def test_set_protobuf_oneof_nooverride():
    xp = Experiment(trainer=Trainer(image_detection=Detection(label_smoothing=0.12345)))
    controls.set_protobuf_oneof(xp, 'image_detection', 'trainer.model_type')
    assert xp.trainer.image_detection.label_smoothing == pytest.approx(0.12345)

def test_set_protobuf_oneof_override():
    xp = Experiment(trainer=Trainer(image_detection=Detection(label_smoothing=0.12345)))
    controls.set_protobuf_oneof(xp, 'image_classification', 'trainer.model_type')
    assert xp.trainer.WhichOneof('model_type') == 'image_classification'
