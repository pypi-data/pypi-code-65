from typing import List, Type
from fancy.descriptor.method_descriptor_base import SimpleMethodDescriptor, MethodDescriptorBase, MethodDescriptor
from fancy.descriptor.tests.unit.method_descriptor_base.fake_descriptor import FakeDescriptor
from fancy.descriptor.tests.unit.method_descriptor_base.fake_marked import FakeMarked


class TestMethodDescriptors:
    fake_marked_instance = FakeMarked()
    expected_returns = {
        "marked_simple_method_descriptor": 0,
        "marked_method_descriptor": 1,
        "marked_fake_descriptor": 2
    }

    def test_simple_method_descriptor(self):
        expected_names = ["marked_simple_method_descriptor"]
        self._assert_method_name_and_returned_value_equals(SimpleMethodDescriptor, expected_names)
        assert isinstance(self.fake_marked_instance.marked_simple_method_descriptor, SimpleMethodDescriptor)

    def test_method_descriptor(self):
        expected_names = ["marked_method_descriptor", "marked_fake_descriptor"]
        self._assert_method_name_and_returned_value_equals(MethodDescriptor, expected_names)
        assert isinstance(self.fake_marked_instance.marked_method_descriptor, MethodDescriptor)

    def test_fake_method_descriptor(self):
        expected_names = ["marked_fake_descriptor"]
        self._assert_method_name_and_returned_value_equals(FakeDescriptor, expected_names)
        assert isinstance(self.fake_marked_instance.marked_fake_descriptor, FakeDescriptor)
        assert self.fake_marked_instance.marked_fake_descriptor.get_value() == 2

    def _assert_method_name_and_returned_value_equals(
            self,
            descriptor_type: Type[MethodDescriptorBase],
            expected_names: List[str]
    ):
        method_dict = descriptor_type.get_marked_method(self.fake_marked_instance)

        assert len(expected_names) == len(method_dict)
        for name in expected_names:
            assert name in method_dict.keys()
            assert method_dict[name]() == self.expected_returns[name]
        return method_dict
