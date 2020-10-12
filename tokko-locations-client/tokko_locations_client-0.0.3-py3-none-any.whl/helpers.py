from contextlib import suppress


class Extends:

    def __init__(self, extended_field, resolve_with_method, target_class):
        self.extended_field_name = extended_field
        self.resolver_name = resolve_with_method
        self.target_class = target_class

    def __call__(self, method):

        def wrapped_f(instance, *args, **kwargs):
            res = method(instance, *args, **kwargs)
            if any(
                [
                    not hasattr(res, self.extended_field_name),
                    # ToDo: Only should runs when
                ]
            ):
                return res

            with suppress(AttributeError):
                resolver = getattr(instance, self.resolver_name, None)
                field_content = getattr(res, self.extended_field_name)
                if isinstance(field_content, self.target_class):
                    setattr(res, self.extended_field_name, resolver(field_content))
            return res

        return wrapped_f
