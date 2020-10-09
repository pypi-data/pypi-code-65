from w.tests.builders.abstract_test_builder import AbstractTestBuilder
from w.tests.fixtures.datasets.builders import factory_boy
from w.tests.fixtures.datasets.builders.models import FakeDjangoModel


class BuilderFakeDjangoModelWithForeignKey(AbstractTestBuilder):
    _factories = {
        "fake_with_fk": factory_boy.FakeDjangoModelWithForeignKeyFactory,
        "fake": factory_boy.FakeDjangoModelFactory,
    }
    _main_factory_key = "fake_with_fk"

    @staticmethod
    def mock_is_django_model(value):
        return isinstance(value, FakeDjangoModel)
