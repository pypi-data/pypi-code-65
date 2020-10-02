"""Decorators for wrapping callback functions and methods."""

import inspect
import types
from functools import partial, update_wrapper

import click


def with_context(func=None, obj_type=None, context_arg='ctx'):
    """
    More flexible alternative to `click.pass_context` and `click.pass_obj`.

    Combines the functionality of both those decorators, but the difference
    is instead of passing the context/context.obj to the first argument of
    the wrapped function, it passes it to specified ``context_arg`` keyword
    argument, where by default ``context_arg='ctx'`` so it can work
    equivalently to `click.pass_context`.

    Examples
    --------

    >>> from objclick import with_context, group
    >>> @group(no_args_is_help=False, invoke_without_command=True)
    ... @with_context
    ... def main(ctx):
    ...     print(ctx)
    ...     ctx.obj = 1
    ...
    >>> main([], standalone_mode=False)
    <click.core.Context object at 0x...>

    Sub-commands can use `with_context` similarly to `click.pass_obj`:

    >>> @main.command()
    ... @with_context(obj_type=int, context_arg='obj')
    ... def subcommand(obj):
    ...     print('subcommand', obj)
    ...
    >>> main(['subcommand'], standalone_mode=False)
    <click.core.Context object at 0x...>
    subcommand 1
    """

    if func is None:
        return partial(with_context, obj_type=obj_type, context_arg=context_arg)

    def context_wrapper(*args, **kwargs):
        ctx = obj = click.get_current_context()
        if isinstance(obj_type, type):
            obj = ctx.find_object(obj_type)

        kwargs[context_arg] = obj
        return ctx.invoke(func, *args, **kwargs)

    update_wrapper(context_wrapper, func)
    return context_wrapper


def command(*args, **kwargs):
    """
    Like `click.group` but wraps methods defined in classes with
    `with_context`, giving the context in ``self``.

    In other words, this allows commands to be defined on methods of a class.
    In order to call those commands, the class must be instantiated, and the
    command called on an instance of the class::

        >>> from objclick import command, argument
        >>> class Foo:
        ...     @command()
        ...     @argument('bar')
        ...     def bar(self, bar):
        ...         print(self, bar)
        ...
        >>> Foo.bar
        <MethodCommand bar>

    Attempting to call ``Foo.bar`` directly will fail, just as though it were
    a normal method::

        >>> Foo.bar(['xyz'])
        Traceback (most recent call last):
        ...
        TypeError: bar() missing 1 required positional argument: 'self'

    But calling it on an instance of ``Foo`` will work, and the instance is
    passed to the ``self`` argument like a normal method::

        >>> Foo().bar(['xyz'], standalone_mode=False)
        <objclick.decorators.Foo object at 0x...> xyz

    Examples
    --------

    It is possible to subclass a class with method commands, and override
    those commands while calling the superclass's command of the same name.
    However, at present this does not copy the superclass command's
    parameters and arguments, so they must be re-stated.  This will be
    improved in a future version.

    There is also presently a limitation to be aware of (again, to be fixed
    in a future version) that when invoking the callback on a superclass
    command, all arguments must be passed as keyword arguments, even if they
    were not declared that way in the original function definition:

    >>> class SubFoo(Foo):
    ...     @command()
    ...     @argument('bar')
    ...     def bar(self, bar):
    ...         super().bar.callback(bar=bar)
    ...         print('additional functionality')
    ...
    >>> SubFoo().bar(['xyz'], standalone_mode=False)
    <objclick.decorators.SubFoo object at 0x...> xyz
    additional functionality
    """

    def decorator(callback):
        sig = inspect.signature(callback).parameters
        cls = kwargs.get('cls', MethodCommand)
        if issubclass(cls, MethodCommand) and cls.context_arg in sig:
            kwargs.setdefault('cls', cls)

        return click.command(*args, **kwargs)(callback)

    return decorator


def group(*args, **kwargs):
    """
    Like `click.group` but wraps methods defined in classes with
    `with_context`, giving the context in ``self``.

    This is the group analogy to `command`--that is, it allows registering
    an instance method as the group callback::

        >>> from objclick import group, argument, option
        >>> class Foo:
        ...      @group(no_args_is_help=False, invoke_without_command=True)
        ...      def main(self):
        ...          print(self)
        ...
        >>> Foo().main([], standalone_mode=False)
        <objclick.decorators.Foo object at 0x...>

    In this example, the ``main`` group can then be used to register
    sub-commands and sub-groups as in normal `click`.  By default these are
    also assumed to be instance methods of the same class::

        >>> class Foo:
        ...      @group(no_args_is_help=False, invoke_without_command=True)
        ...      def main(self):
        ...          print(self)
        ...
        ...      @main.command()
        ...      @argument('name')
        ...      def hello(self, name):
        ...          print(f'Hello {name}, I am a {self}')
        ...
        >>> Foo().main(['hello', 'Fred'], standalone_mode=False)
        <objclick.decorators.Foo object at 0x...>
        Hello Fred, I am a <objclick.decorators.Foo object at 0x...>

    Also supports decorating classes to create a command group.  In this
    case the wrapped class becomes a group, and all methods in the class
    decorated with `command` or `group` are added as sub-commands.

    If the decorated class has a ``__call__`` method it is used as the
    group's callback function.  Otherwise a no-op callback is generated.

    >>> from objclick import group, command
    >>> @group()
    ... class foo:
    ...     @command()
    ...     @option('--name', default='Fred')
    ...     def hello(self, name):
    ...         print(f'Hello {name}!')
    ...
    >>> foo(['hello', '--name', 'Barney'], standalone_mode=False)
    Hello Barney!

    Examples
    --------

    It is also possible to register non-method commands on a group defined
    from a method.  In this case the wrapped callback will just be treated as
    a normal function, and is not passed ``self``:

    >>> class Foo:
    ...      @group(no_args_is_help=False, invoke_without_command=True)
    ...      def main(self):
    ...          print(self)
    ...
    >>> @Foo.main.command()
    ... @argument('name')
    ... def hello(name):
    ...     print(f'Hello {name}!')
    ...
    >>> Foo().main(['hello', 'Fred'], standalone_mode=False)
    <objclick.decorators.Foo object at 0x...>
    Hello Fred!

    This is effectively analogous to calling a normal function from an instance
    method.

    It is also possible, albeit slightly pathological, to register a method on
    another class as a command associated with a group.  In this case an
    instance of the class the *group* was defined on will be passed to
    ``self``:

    >>> class Foo:
    ...      @group(no_args_is_help=False, invoke_without_command=True)
    ...      def main(self):
    ...          print(self)
    ...
    >>> class Bar:
    ...      @Foo.main.command()
    ...      @argument('name')
    ...      def hello(self, name):
    ...          print(f'Hello {name}, I am a {self}')
    ...
    >>> Foo().main(['hello', 'Fred'], standalone_mode=False)
    <objclick.decorators.Foo object at 0x...>
    Hello Fred, I am a <objclick.decorators.Foo object at 0x...>

    This is similar to doing something like ``Bar.hello(self, name)`` from
    within a method of ``Foo``.  Unusual (since ``self`` is an instance of the
    wrong class), but doable.  This example is just to demonstrate that
    chaining commands defined on instance methods works similarly to calling
    normal instance methods in Python and is not particularly "magic".
    """

    def decorator(callback):
        if isinstance(callback, type):
            # Implement @group() on classes
            cls = callback

            if (hasattr(cls, '__call__') and
                    isinstance(cls.__call__, types.FunctionType)):
                callback = cls.__call__
            else:
                callback = lambda self: None

            if not kwargs.get('name'):
                kwargs['name'] = cls.__name__

            if not kwargs.get('help'):
                kwargs['help'] = cls.__doc__

            commands = kwargs.setdefault('commands', {})
            # command() is used in the class to define any commands
            # in the group; this will add those commands to the Group
            # object when it's created
            commands.update({c.name: c for c in vars(cls).values()
                             if isinstance(c, click.BaseCommand)})

            kwargs.setdefault('cls', MethodGroup)
            cls.__call__ = click.group(*args, **kwargs)(callback)
            return cls().__call__

        sig = inspect.signature(callback).parameters
        cls = kwargs.get('cls', MethodGroup)
        if issubclass(cls, MethodCommand) and cls.context_arg in sig:
            kwargs.setdefault('cls', cls)

        return click.group(*args, **kwargs)(callback)

    return decorator


def classcommand(*args, **kwargs):
    """
    Like `command`, but for class-bound methods.  This is analogous to
    composing `command` with `classmethod`.

    In this case the the first argument of the callback method is bound to
    the class, not an instance of the class, and so the command can be called
    without instantiating the class::

        >>> from objclick import classcommand, argument
        >>> class Foo:
        ...     @classcommand()
        ...     @argument('name')
        ...     def hello(cls, name):
        ...         print(cls)
        ...         print(f'Hello {name}!')
        ...
        >>> Foo.hello(['Tony'], standalone_mode=False)
        <class 'objclick.decorators.Foo'>
        Hello Tony!

    Examples
    --------

    Regression test: It should be possible to call a parent class's
    `classcommand` callback from a subclass:

    >>> from objclick import classcommand
    >>> class Foo:
    ...     @classcommand()
    ...     def main(cls):
    ...         print('Foo.main', cls)
    ...
    >>> class Bar(Foo):
    ...     @classcommand()
    ...     def main(cls):
    ...         super().main.callback()
    ...         print('Bar.main', cls)
    ...
    >>> Bar.main([], standalone_mode=False)
    Foo.main <class 'objclick.decorators.Bar'>
    Bar.main <class 'objclick.decorators.Bar'>
    """

    kwargs.setdefault('cls', ClassMethodCommand)
    return command(*args, **kwargs)


def classgroup(*args, **kwargs):
    """
    Alternative to `click.group` which allows a command group to be declared
    on a class-bound method, similarly to a composition of `click.group` and
    `classmethod`.

    It is possible for instance methods of the same class to be added as
    subcommands and subgroups to a classgroup.  But this requires some special
    handling: Because calling a `classmethod` (and hence a classgroup) does
    not require instantiating the class, how should instance methods chained
    from the classgroup get an instance of the class?

    It is a typical pattern to use a `classmethod` as an alternative
    constructor for a class.  In this case the `classmethod` would return an
    instance of the class.  If `classgroup` is used to decorator such a
    method--whose return value is an instance of the class it's defined on--
    then that instance will be passed as the ``self`` to all subcommands added
    to the group::

        >>> from objclick import classgroup
        >>> class Foo:
        ...     @classgroup(no_args_is_help=False, invoke_without_command=True)
        ...     def main(cls):
        ...         print(cls)
        ...         return cls()
        ...
        ...     @main.command()
        ...     def subcommand(self):
        ...         print('subcommand', self)
        ...
        >>> Foo.main(['subcommand'], standalone_mode=False)
        <class 'objclick.decorators.Foo'>
        subcommand <objclick.decorators.Foo object at 0x...>

    Examples
    --------

    It is also possible to chain additional classmethods as
    subcommands/subgroups of a `classgroup`:

    >>> from objclick import classgroup
    >>> class Foo:
    ...     @classgroup(no_args_is_help=False, invoke_without_command=True)
    ...     def main(cls):
    ...         print(cls)
    ...         return cls()
    ...
    ...     @main.classcommand()
    ...     def subcommand(cls):
    ...         print('subcommand', cls)
    ...
    >>> Foo.main(['subcommand'], standalone_mode=False)
    <class 'objclick.decorators.Foo'>
    subcommand <class 'objclick.decorators.Foo'>

    If the method wrapped by `classgroup` does *not* return an instance of the
    class, it is still possible in that method to create an instance of the
    class and set it as the context to be passed down to subcommands by using
    `with_context` explicitly:

    >>> from objclick import classgroup, with_context
    >>> class Foo:
    ...     @classgroup(no_args_is_help=False, invoke_without_command=True)
    ...     @with_context
    ...     def main(cls, ctx):
    ...         print(cls)
    ...         print(ctx)
    ...         ctx.obj = cls()
    ...         print(ctx.obj)
    ...
    ...     @main.command()
    ...     def subcommand(self):
    ...         print('subcommand', self)
    ...
    >>> Foo.main([], standalone_mode=False)
    <class 'objclick.decorators.Foo'>
    <click.core.Context object at 0x...>
    <objclick.decorators.Foo object at 0x...>

    >>> Foo.main(['subcommand'], standalone_mode=False)
    <class 'objclick.decorators.Foo'>
    <click.core.Context object at 0x...>
    <objclick.decorators.Foo object at 0x...>
    subcommand <objclick.decorators.Foo object at 0x...>

    You can still attach non-method subcommands to the group ``Foo.main`` as
    usual:

    >>> @Foo.main.command()
    ... @with_context(obj_type=Foo, context_arg='foo')
    ... def subcommand2(foo):
    ...     print('subcommand2', foo)
    ...
    >>> Foo.main(['subcommand2'], standalone_mode=False)
    <class 'objclick.decorators.Foo'>
    <click.core.Context object at 0x...>
    <objclick.decorators.Foo object at 0x...>
    subcommand2 <objclick.decorators.Foo object at 0x...>

    The `click.Group` object, and by extension any sub-commands added to it,
    are bound to each class on which it's accessed, so subclasses do not
    inherit any method commands added to the group, but not non-method
    commands:

    >>> Foo.main.commands
    {'subcommand': <MethodCommand subcommand>,
     'subcommand2': <Command subcommand2>}
    >>> class Bar(Foo): pass
    >>> Bar.main.commands
    {'subcommand': <MethodCommand subcommand>}
    """

    kwargs.setdefault('cls', ClassMethodGroup)
    return command(*args, **kwargs)


# Late imports due to import cycle
from .objclick import (MethodCommand, MethodGroup, ClassMethodCommand,
        ClassMethodGroup)
