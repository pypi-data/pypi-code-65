from fancy.descriptor.method_descriptor_base import SimpleMethodDescriptor
from fancy.descriptor.method_descriptor_factories import SimpleMethodDescriptorFactory


class TestMethodDescriptorFactories:

    def test_create(self):
        assert isinstance(SimpleMethodDescriptorFactory().create(lambda x: x), SimpleMethodDescriptor)
