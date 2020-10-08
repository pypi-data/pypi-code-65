from aiida.engine import WorkChain
from aiida import orm
class Top(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('a', valid_type=orm.Int, required=True)
        spec.input('b', valid_type=orm.Int, required=False)
        spec.outline(cls.run)
    def run(self):
        pass
class Bottom(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('c', valid_type=orm.Int, required=True)
        spec.expose_inputs(Top, namespace='top', include=('a',), namespace_options={'required': False, 'populate_defaults': False})
        spec.outline(cls.run)
    def run(self):
        pass



import pytest
from aiida_testing.export_cache._fixtures import run_with_cache, export_cache, load_cache, hash_code_by_entrypoint
from aiida.manage.tests.pytest_fixtures import aiida_profile, clear_database, clear_database_after_test
from .conftest import data_dir

def test_namespace_options(aiida_profile, run_with_cache):
    b = Bottom.get_builder()
    b.c = orm.Int(1)
    run_with_cache(b, data_dir=data_dir)