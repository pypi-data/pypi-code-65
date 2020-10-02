"""Some utilities for extending the functionality of `click`."""

import copy
import weakref
from functools import update_wrapper

import click

from .decorators import (with_context, command, group, classcommand,
        classgroup)


class MethodCommand(click.Command):
    bound = False
    obj_type = object
    context_arg = 'self'

    def __get__(self, obj, owner=None):
        if obj is None:
            return self

        # Support super() binding: Now here's the tricky thing:
        # when calling super().some_command this means `self` will *not*
        # be the MethodCommand in owner.__dict__['some_command'], but
        # rather will be the 'some_command' found in the first class in
        # owner's __mro__ (i.e. the subclass it inherited 'some_command'
        # from.  We can detect this by checking if `self` is
        # owner.__dict__[self.name].  If not, we just return the superclass's
        # MethodCommand
        if (owner is not None and self.name in owner.__dict__ and
                owner.__dict__[self.name] is not self):
            return self.bind(obj)

        key = '_' + self.name
        # The bound command instance is cached in the owner's dict
        bound_command = obj.__dict__.get(key)

        if bound_command is None or bound_command() is None:
            bound_command = self.bind(obj)
            setattr(obj, key, weakref.ref(bound_command))
            return bound_command

        return bound_command()

    def __repr__(self):
        s = super().__repr__()
        if self.bound:
            s = s.replace(self.__class__.__name__,
                          'bound ' + self.__class__.__name__, 1)

        return s

    def bind(self, obj=None):
        bound_command = copy.deepcopy(self)
        callback = with_context(bound_command.callback, self.obj_type,
                                self.context_arg)

        if obj is not None:
            def with_context_obj(callback):
                def wrapper(*args, **kwargs):
                    ctx = click.get_current_context()
                    ctx.obj = obj
                    return callback(*args, **kwargs)

                update_wrapper(wrapper, callback)
                return wrapper

            callback = with_context_obj(callback)

        bound_command.callback = callback
        bound_command.bound = True
        return bound_command

    def make_context(self, info_name, args, parent=None, **extra):
        if parent is not None:
            extra['obj'] = parent.meta.pop('self', extra.get('obj'))

        return super().make_context(info_name, args, parent=parent, **extra)


class MethodGroup(MethodCommand, click.Group):
    def __init__(self, name, **kwargs):
        self._init_kwargs = kwargs
        super().__init__(name, **kwargs)

    def copy(self, **kwargs):
        init_kwargs = self._init_kwargs.copy()
        init_kwargs.update(kwargs)
        init_kwargs.setdefault('callback', self.callback)
        init_kwargs.setdefault('commands', self.commands)
        return self.__class__(self.name, **init_kwargs)

    def command(self, *args, **kwargs):
        """
        Registers a sub-command on this group in a way intended to be used on
        instance methods of the class this `MethodGroup` is defined on.

        In this case the ``self`` argument of the method is passed ``ctx.obj``,
        which is assumed to be an instance of the class that the `MethodGroup`
        is defined on.  See the documentation for `group` for an example.

        Examples
        --------

        >>> from objclick import group, option
        >>> class Foo:
        ...     @group()
        ...     def main(self):
        ...         print(self)
        ...
        ...     @main.command()
        ...     @option('--bar')
        ...     def subcommand(self, bar):
        ...         print('subcommand self', self)
        ...         print('subcommand bar', bar)
        ...
        >>> Foo().main(['subcommand', '--bar', 'qux'], standalone_mode=False)
        <objclick.objclick.Foo object at 0x...>
        subcommand self <objclick.objclick.Foo object at 0x...>
        subcommand bar qux
        """

        def decorator(callback):
            cmd = command(*args, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        """
        A shortcut decorator for declaring and attaching a subgroup to this
        group.

        Works analogously to `MethodGroup.command`.
        """

        def decorator(callback):
            cmd = group(*args, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator

    def get_command(self, ctx, cmd_name):
        cmd = super().get_command(ctx, cmd_name)
        if self.bound and isinstance(cmd, MethodCommand):
            cmd = cmd.bind(obj=ctx.obj)
        return cmd


class ClassMethodCommand(MethodCommand):
    obj_type = type
    context_arg = 'cls'

    def __get__(self, obj, owner=None):
        return super().__get__(owner, owner=owner)


class ClassMethodGroup(ClassMethodCommand, MethodGroup):
    def classcommand(self, *args, **kwargs):
        """
        Register a class-bound subcommand.

        Examples
        --------

        >>> from objclick import classgroup
        >>> class Foo:
        ...     @classgroup()
        ...     def main(cls):
        ...          print(cls)
        ...
        ...     @main.classcommand()
        ...     def subcommand(cls):
        ...         print('subcommand', cls)
        ...
        >>> Foo.main(['subcommand'], standalone_mode=False)
        <class 'objclick.objclick.Foo'>
        subcommand <class 'objclick.objclick.Foo'>
        """

        def decorator(callback):
            cmd = classcommand(*args, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator

    def classgroup(self, *args, **kwargs):
        """
        Like `ClassMethodGroup.classcommand` but for registering a class-bound
        subgroup.
        """

        def decorator(callback):
            cmd = classgroup(*args, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator

    def command(self, *args, **kwargs):
        """
        Registers a sub-command on this group in a way intended to be used on
        instance methods of the class this `MethodGroup` is defined on.

        In this case the ``self`` argument of the method is passed ``ctx.obj``,
        which is assumed to be an instance of the class that the `MethodGroup`
        is defined on.

        Examples
        --------

        >>> from objclick import classgroup, option
        >>> class Foo:
        ...     @classgroup(no_args_is_help=False, invoke_without_command=True)
        ...     def main(cls):
        ...         print(cls)
        ...         return cls()
        ...
        ...     @main.command()
        ...     @option('--bar')
        ...     def subcommand(self, bar):
        ...         print('subcommand self', self)
        ...         print('subcommand bar', bar)
        ...
        >>> Foo.main(['subcommand', '--bar', 'qux'], standalone_mode=False)
        <class 'objclick.objclick.Foo'>
        subcommand self <objclick.objclick.Foo object at 0x...>
        subcommand bar qux
        """

        return super().command(*args, **kwargs)

    def bind(self, obj=None):
        # Add additional wrapper around the group's callback to capture its
        # return value in ctx.meta['self']
        # Because of how the group callback is normally invoked, there isn't
        # otherwise a great way to capture it.
        bound_command = super().bind(obj)
        callback = bound_command.callback

        def capture_result_wrapper(*args, **kwargs):
            ctx = click.get_current_context()
            rv = callback(*args, **kwargs)
            if isinstance(rv, obj):
                ctx.meta['self'] = rv
            return rv

        update_wrapper(capture_result_wrapper, callback)
        bound_command.callback = capture_result_wrapper
        return bound_command
