from fancy.descriptor.tests.unit.method_descriptor_factories.fake_method_descriptor_factory import \
    FakeMethodDescriptorFactory


class TestMethodDescriptorFactoryBase:
    def test_singleton(self):
        assert FakeMethodDescriptorFactory() is FakeMethodDescriptorFactory()
