from fancy.descriptor.method_descriptor_base import MethodDescriptor, SimpleMethodDescriptor
from fancy.descriptor.tests.unit.method_descriptor_base.fake_descriptor import FakeDescriptor


class FakeMarked:

    @SimpleMethodDescriptor
    def marked_simple_method_descriptor(self):
        return 0

    @MethodDescriptor
    def marked_method_descriptor(self):
        return 1

    @FakeDescriptor.bind(value=2)
    def marked_fake_descriptor(self):
        return 2
