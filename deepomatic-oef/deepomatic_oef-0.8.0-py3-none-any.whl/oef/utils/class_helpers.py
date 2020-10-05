from enum import Enum
import importlib

serializer_class = None  # this is a small hack to delay the loading of the Serializer class to break an import loop (serializer.py loads class_helper)

api_prefix = 'deepomatic.oef.'
api_proto_prefix = api_prefix + 'protos.'
proto_suffix = '_pb2'

class ClassType(Enum):
    PROTO = api_proto_prefix
    API = api_prefix

# -----------------------------------------------------------------------------#

def split_path_into_module_and_class(path):
    """
    By convention, classes start with a capital letter and modules only have small letters.
    We use that to split a path into module and class
    """
    module = []
    classes = []
    path = path.split('.')
    for i, part in enumerate(path):
        if part[0].isupper():
            classes = path[i:]
            break
        module.append(part)
    module = '.'.join(module)
    return module, classes

# -----------------------------------------------------------------------------#

def get_normalized_module_and_classes(path):
    """
    Get the normalized (non back-end, without '_pb2') module name and class names from a path.
    E.g. deepomatic.oef.Model.SubClass would return ('model', ['Model', 'SubClass'])
    """

    # Be careful, the order of the if branch matters
    if path.startswith(api_proto_prefix):
        path = path.replace(api_proto_prefix, '')
        module, classes = split_path_into_module_and_class(path)
        if module.endswith(proto_suffix):
            module = module[:-len(proto_suffix)]
        return module, classes
    elif path.startswith(api_prefix):
        path = path.replace(api_prefix, '')
    else:
        raise Exception("Unexpected path type, does not start with any known prefix: '{}'".format(path))

    return split_path_into_module_and_class(path)

# -----------------------------------------------------------------------------#

def convert_module_path(path, to_type):
    """
    Takes a normalized module `path` and convert it to a specialized path of type `to_type`
    Args:
        path (string): a module path, normalized by get_normalized_module_and_classes
        to_type (ClassType): an enum of type ClassType

    Returns:
        string: The specialized module path.
    """
    path = to_type.value + path
    if to_type == ClassType.PROTO:
        path += proto_suffix
    return path


# -----------------------------------------------------------------------------#

def load_class(module, classes, getter=getattr):
    """Load class from module path and a list of nested classes"""
    class_container = importlib.import_module(module)
    for c in classes:
        class_container = getter(class_container, c)
    return class_container


# -----------------------------------------------------------------------------#

def load_proto_class_from_protobuf_descriptor(descriptor, class_type=ClassType.PROTO, getter=getattr):
    """
    Given a protobuf message descriptor, return its associated class: either the protobuf or the serializer
    """
    # We first extract the class name: careful as it may be nested messages.
    # For exemple: descriptor.full_name is `deepomatic.oef.models.image.backbones.EfficientNetBackbone.Version`
    # descriptor.file.package is `deepomatic.oef.models.image.backbones`
    # So field_type is `EfficientNetBackbone.Version`
    namespace_prefix = descriptor.file.package + '.'
    assert descriptor.full_name.startswith(namespace_prefix), "Field type should normally start with '{}'".format(namespace_prefix)
    classes = descriptor.full_name.replace(descriptor.file.package + '.', '')

    # Find the module name
    module_path = descriptor.file.name
    assert module_path.endswith('.proto'), "File type should normally end with '.proto'"
    module_path = module_path.replace('.proto', '').replace('/', '.')  # order matters for the replace
    assert module_path.startswith(api_proto_prefix), "Package should normally start with '{}'".format(api_proto_prefix)
    module_path = module_path.replace(api_proto_prefix, '')

    module_path = convert_module_path(module_path, class_type)
    return load_class(module_path, classes.split('.'), getter=getter)

# -----------------------------------------------------------------------------#
