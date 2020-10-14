# -*- coding: utf-8 -*-
from _pytest.compat import getfuncargnames
from _pytest.python import FunctionDefinition, Class
from _pytest.fixtures import FixtureDef, scopes, FixtureLookupError


def pytest_addoption(parser):
    group = parser.getgroup('missing-fixtures')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2020',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo


def pytest_pycollect_makeitem(collector, name, obj):
    """
    @fixture('session')
    def a():
        pass

    Session fixtures _a, _b(_a)
    Function fixture _a

    def test_some(b)

    """

    # if first_time:
    #     global first_time
    #     first_time = False
    #
    #     import IPython; IPython.start_ipython(argv=[], user_ns=dict(locals()))

    if not collector.istestfunction(obj, name):
        return

    fixture_manager = collector.session._fixturemanager
    # fixture_defs = item._request._arg2fixturedefs

    # def func_fixture_def(argname, nodeid):


    definition = FunctionDefinition(name, parent=collector, callobj=obj)
    nodeid = definition.nodeid

    baseid = definition.parent.nodeid


    def lift_up_fixture_def(arg_names):

        arg_deps_max_scope = 0
        for arg_name in arg_names:
            fixture_defs = fixture_manager.getfixturedefs(arg_name, nodeid)

            if fixture_defs:
                fixture_def = fixture_defs[-1]
            else:
                raise LookupError(arg_name)

            arg_max_scope = lift_up_fixture_def(fixture_def.argnames)
            if fixture_def.scopenum < arg_max_scope:
                fixture_manager._arg2fixturedefs[arg_name] += [
                    FixtureDef(fixture_manager, baseid=baseid, argname=arg_name, func=fixture_def.func,
                               scope=scopes[arg_max_scope], params=None),
                ]
                pass

            arg_deps_max_scope = max(arg_deps_max_scope, arg_max_scope, fixture_def.scopenum)
            # arg_deps_max_scope = max(arg_deps_max_scope, arg_max_scope)

        return arg_deps_max_scope

    clscol = collector.getparent(Class)
    cls = clscol.obj if clscol else None

    arg_names = getfuncargnames(obj, cls=cls)

    lift_up_fixture_def(arg_names)

# Func fixtures
# + It's simple
# - Slow tear up
# - Can not upper last chained fixtures

#

# pytest.skip('No Redis server found')

