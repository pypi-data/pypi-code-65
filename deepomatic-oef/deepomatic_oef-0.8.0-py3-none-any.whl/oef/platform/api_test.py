import os
import pytest
from pytest import approx
import random

from deepomatic.oef.configs.model_list import model_list
from .helpers.tags import ViewType

from . import api

def get_model_list(default_payload):
    model_property_name = default_payload['model_property_name']
    for section in default_payload['sections']:
        for control in section['controls']:
            if control['property'] == model_property_name:
                return [v['value'] for v in control['control_parameters']['values']]
    raise Exception('models not found')


@pytest.mark.parametrize(
    'view_type', ViewType
)
def test_default_models_format(view_type):
    """
    WARNING: if you have to change this test, it is very likely that you have to
             change the front-end that generates the form.
    """
    properties = set()
    tags = set()
    all_display_ifs = []

    def check_tags(property_name, declared_tags):
        nonlocal tags
        declared_tags = set(declared_tags)
        assert property_name in declared_tags
        assert len(tags & declared_tags) == 0
        tags = tags | declared_tags
        return True

    # Check root format
    default = api.get_default_models(view_type)
    assert 'model_property_name' in default and default['model_property_name']
    assert 'default_model' in default
    assert 'sections' in default and default['sections']
    assert 'default_values' in default
    assert 'value_to_tag_map' in default

    # Check sections
    for section in default['sections']:
        assert 'name' in section and section['name']
        assert 'controls' in section and section['controls']

        for control in section['controls']:
            assert 'message' in control and control['message']
            assert 'type' in control and control['type'] in ['select', 'input', 'toggle']
            assert 'property' in control and control['property']
            assert control['property'] not in properties
            properties.add(control['property'])
            assert 'display_if' in control
            all_display_ifs.append((control['property'], control['display_if']))
            assert 'control_parameters' in control  # may be null for toggle

            assert 'tags' in control
            if control['type'] == 'select':
                assert control['tags'] is not None and check_tags(control['property'], control['tags'])
                assert 'values' in control['control_parameters']
                for value in control['control_parameters']['values']:
                    assert 'value' in value and isinstance(value['value'], str)
                    assert 'display_string' in value and isinstance(value['display_string'], str)
                    assert 'display_if' in value
                    all_display_ifs.append((control['property'], value['display_if']))

            elif control['type'] == 'input':
                assert control['tags'] is None  # must be null for input
                assert 'min_value' in control['control_parameters']
                assert 'max_value' in control['control_parameters']
                assert 'increment_value' in control['control_parameters']
                if control['control_parameters']['min_value'] is not None and control['control_parameters']['max_value'] is not None:
                    assert control['control_parameters']['min_value'] < control['control_parameters']['max_value']

            elif control['type'] == 'toggle':
                assert control['tags'] is not None and check_tags(control['property'], control['tags'])
                assert control['control_parameters'] is None

            else:
                raise Exception("Unexpected control type: {}".format(control['type']))

    for property_name, display_ifs in all_display_ifs:
        for display_if in display_ifs:
            ok = 'tag' in display_if and display_if['tag'] in tags
            ok = ok and 'allowed_values' in display_if and len(display_if['allowed_values']) > 0
            if not ok:
                raise Exception("Error with display_if condition for control '{}': display_if not respecting format: {}".format(property_name, display_if))

    # Check default_values
    models = get_model_list(default)
    assert set(models) == default['default_values'].keys()
    for default_values in default['default_values'].values():
        # Check that all properties have been declared
        assert len(default_values.keys() - properties) == 0

    # Check value_to_tag_map
    for section in default['sections']:
        for control in section['controls']:
            if control['type'] == 'select':
                values = [v['value'] for v in control['control_parameters']['values']]
            elif control['type'] == 'toggle':
                values = ['false', 'true']
            elif control['type'] in ['input']:
                continue  # we do nothing
            else:
                raise Exception("Unexpected control type: {}".format(control['type']))

            assert control['property'] in default['value_to_tag_map']
            value_to_tag_map = default['value_to_tag_map'][control['property']]
            if control['property'] == default['model_property_name']:
                assert value_to_tag_map.keys() > set(values)
            else:
                assert value_to_tag_map.keys() == set(values)
            for tags in value_to_tag_map.values():
                assert tags.keys


@pytest.mark.parametrize(
    'view_type', ViewType
)
def test_default_models_are_valid(view_type):
    default = api.get_default_models(view_type)
    models = get_model_list(default)
    assert default['default_model'] in models
    assert default['default_model'] in model_list
    for model in models:
        assert model in model_list


@pytest.mark.parametrize(
    'view_type', ViewType
)
def test_random_protobuf_from_post_request(view_type):
    config = api.get_default_models(view_type)
    for i in range(10):  # repeat 10 times
        payload = {}
        for section in config['sections']:
            for control in section['controls']:
                if control['type'] == 'select':
                    value = random.choice(control['control_parameters']['values'])['value']
                elif control['type'] == 'input':
                    start = -100000000000
                    stop  = 100000000000
                    if 'min_value' in control['control_parameters']:
                        start = control['control_parameters']['min_value']
                    if 'max_value' in control['control_parameters']:
                        stop = control['control_parameters']['max_value']
                    value = random.uniform(start, stop)
                    if 'increment_value' in control['control_parameters']:
                        increment_value = control['control_parameters']['increment_value']
                        # The input seems to be a int input
                        if increment_value == int(increment_value):
                            value = int(value)
                elif control['type'] == 'toggle':
                    value = random.choice([False, True])
                else:
                    raise Exception('Unexpected control type: {}'.format(control['type']))
                payload[control['property']] = value
        # This relies on the fact that the model builder in parse_experiment
        # will complain if some value are unsed in the payload
        try:
            api.parse_experiment(payload)
        except Exception as e:
            raise Exception("Building the experiment protobuf with payload '{}' failed with {}".format(payload, str(e)))


def test_hand_picked_protobuf_from_post_request_tensorflow():
    payload = {
        'model': 'image_classification.pretraining_natural_rgb.softmax.efficientnet_b4',
        'trainer.num_train_steps': 1234,
        'trainer.initial_learning_rate': 0.0456,
        'optimizer': 'momentum_optimizer',
        'trainer.optimizer.momentum_optimizer.momentum_optimizer_value': 0.8,
        'trainer.optimizer.rms_prop_optimizer.momentum_optimizer_value': 0.7,  # front-end will send all values
        'trainer.optimizer.rms_prop_optimizer.decay': 0.6,
        'trainer.optimizer.rms_prop_optimizer.epsilon': 0.5,
        'balance': 'true'
    }
    check_payload_is_valid(payload)

    xp = api.parse_experiment(payload)
    assert xp.trainer.WhichOneof('model_type') == 'image_classification'
    assert xp.trainer.num_train_steps == 1234
    assert xp.trainer.initial_learning_rate == approx(0.0456)
    assert 'efficientnet' in xp.trainer.pretrained_parameters
    assert xp.trainer.optimizer.WhichOneof('optimizer') == 'momentum_optimizer'
    assert xp.trainer.optimizer.momentum_optimizer.momentum_optimizer_value == approx(0.8)
    assert len(xp.dataset.operations) == 1
    assert xp.dataset.operations[0].WhichOneof('operation_type') == 'loss_based_balancing'

    payload['optimizer'] = 'rms_prop_optimizer'
    payload['balance'] = False
    check_payload_is_valid(payload)

    xp = api.parse_experiment(payload)
    assert xp.trainer.optimizer.WhichOneof('optimizer') == 'rms_prop_optimizer'
    assert xp.trainer.optimizer.rms_prop_optimizer.momentum_optimizer_value == approx(0.7)
    assert xp.trainer.optimizer.rms_prop_optimizer.decay == approx(0.6)
    assert xp.trainer.optimizer.rms_prop_optimizer.epsilon == approx(0.5)
    assert len(xp.dataset.operations) == 0

    payload = {
        'model': 'image_detection.pretraining_natural_rgb.yolo_v3.darknet_53',
        'trainer.num_train_steps': 5678,
        'trainer.initial_learning_rate': 0.0123,
        'optimizer': 'rms_prop_optimizer',
        'trainer.optimizer.momentum_optimizer.momentum_optimizer_value': 0.8,
        'trainer.optimizer.rms_prop_optimizer.momentum_optimizer_value': 0.7,  # front-end will send all values
        'trainer.optimizer.rms_prop_optimizer.decay': 0.6,
        'trainer.optimizer.rms_prop_optimizer.epsilon': 0.5,
        'balance': False
    }
    check_payload_is_valid(payload)

    xp = api.parse_experiment(payload)
    assert xp.trainer.WhichOneof('model_type') == 'image_detection'
    assert xp.trainer.num_train_steps == 5678
    assert xp.trainer.initial_learning_rate == approx(0.0123)
    assert 'darknet53' in xp.trainer.pretrained_parameters
    # this is not a typo: optimizer field for Yolo is invisible and the values should not be parsed
    assert xp.trainer.optimizer.WhichOneof('optimizer') == 'momentum_optimizer'


def check_payload_is_valid(payload):
    fields = payload.keys()
    form_fields = set()
    for section in api.form.sections:
        for control in section.controls:
            form_fields.add(control.property_name)
    if fields != form_fields:
        raise Exception('The test payload is not up-to-date: unknown test field: [{}], missing fields: [{}]'.format(', '.join(fields - form_fields), ', '.join(form_fields - fields)))
