import copy
import logging
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
import google.protobuf.json_format as json_format

from deepomatic.oef.configs import model_list
from deepomatic.oef.utils.serializer import Serializer
from deepomatic.oef.utils.class_helpers import load_proto_class_from_protobuf_descriptor
from deepomatic.oef.protos.experiment_pb2 import Experiment

logger = logging.getLogger(__name__)


class InvalidNet(Exception):
    pass


class ExperimentBuilder(object):
    """
    This class can build a Experiment protobuf given the pre-determined parameters. You can also pass
    additionnal parameters to override the default arguments. In that purpose, all fields of Model and its
    sub-messages are assumed to have a different name (this assumpition is checked by model_generator).
    """

    _model_list = None

    def __init__(self, model_type_key):
        if self._model_list is None:
            self.load_model_list()
        if model_type_key not in self._model_list:
            # Try model_type_key reordering to provide backward compatibility with oef<0.5.0
            model_type_key_parts = model_type_key.split('.')
            model_type_key_new_format = '.'.join([model_type_key_parts[0], model_type_key_parts[-1]] + model_type_key_parts[1:-1])
            if model_type_key_new_format in self._model_list:
                logger.warning("This model key format is deprecated: '{}'. Use '{}' instead.".format(model_type_key, model_type_key_new_format))
                model_type_key = model_type_key_new_format
            else:
                raise InvalidNet("Unknown model key '{}'. Also tried '{}' for backward compatibility.".format(model_type_key, model_type_key_new_format))
        self._model_args = self._model_list[model_type_key]

    def get_model_param(self, param):
        """
        Search in args and default_args for `param`. This permits searching for a default parameter
        from the model_list, after an Experiment has been built.
        Warning: this should be used as a last resort, when you need a param from an Experiment, before even building it.
        ```
        builder = ExperimentBuilder(...)
        batch_size = builder.get_model_param('batch_size')
        xp = builder.build(num_train_steps = n / batch_size)
        ```
        All protobuf default params are exposed once it's built.
        """
        if param in self._model_args.default_args:
            return self._model_args.default_args[param]
        else:
            logger.warn('Parameter not found in experiment builder: {}. Available model args are: {}'.format(param, self._model_args))

    @classmethod
    def load_model_list(cls):
        # Avoid to load it at the root of the module to avoid nested import loops
        cls._model_list = {}
        for key, args in model_list.model_list.items():
            assert key not in cls._model_list, "Duplicate model key, this should not happen"
            cls._model_list[key] = args

    def build(self, **kwargs):
        all_args = set()
        all_args.update(self._model_args.default_args.keys())
        all_args.update(kwargs.keys())
        used_args = set()
        kwargs = copy.deepcopy(kwargs)
        xp = self._recursive_build_(Experiment, self._model_args.default_args, kwargs, used_args)
        unused_args = all_args - used_args
        if len(unused_args) > 0:
            raise Exception('Unused keyword argument: {}'.format(', '.join(unused_args)))
        return xp

    @staticmethod
    def _recursive_build_(protobuf_class, default_args, kwargs, used_args):
        real_args = {}

        unsed_default_args = default_args.keys() - set([f.name for f in protobuf_class.DESCRIPTOR.fields])
        if len(unsed_default_args) > 0:
            raise Exception('Unexpected default keyword argument: {}'.format(', '.join(unsed_default_args)))

        def convert_to_dict(value):
            """Convert a serialier into a protobuf"""
            if isinstance(value, Serializer):
                value = value._msg
            if isinstance(value, Message):
                value = json_format.MessageToDict(value, including_default_value_fields=True, preserving_proto_field_name=True)
            return value

        # This dict will be used to check that a oneof is not set twice
        oneof_set = {oneof.name: False for oneof in protobuf_class.DESCRIPTOR.oneofs}

        for field in protobuf_class.DESCRIPTOR.fields:
            # If the field is a scalar or a list ...
            if field.message_type is None or field.label == FieldDescriptor.LABEL_REPEATED:
                # ... there is only one possible value and kwargs has higher priority
                if field.name in kwargs:
                    real_args[field.name] = convert_to_dict(kwargs.pop(field.name))
                elif field.name in default_args:
                    real_args[field.name] = default_args[field.name]

            else:
                # If the field is required, we build it
                if field.name in kwargs or field.name in default_args or field.label == FieldDescriptor.LABEL_REQUIRED:
                    # --> then we build the message
                    args = {}
                    if field.name in kwargs:
                        args = convert_to_dict(kwargs.pop(field.name))
                    elif field.name in default_args:
                        args = default_args[field.name]
                    # This fields is a protobuf message, we build it recursively
                    field_message_class = load_proto_class_from_protobuf_descriptor(field.message_type)
                    real_args[field.name] = ExperimentBuilder._recursive_build_(field_message_class, args, kwargs, used_args)

            if field.containing_oneof is not None and field.name in real_args:
                # The field has a value and belongs to a oneof.
                # We check if the one-of is already set
                oneof_name = field.containing_oneof.name
                assert not oneof_set[oneof_name], "Two values are given for the one-of '{}' (error when processing '{}')".format(oneof_name, field.name)
                oneof_set[oneof_name] = True

        for field_name in real_args:
            used_args.add(field_name)
        return protobuf_class(**real_args)
