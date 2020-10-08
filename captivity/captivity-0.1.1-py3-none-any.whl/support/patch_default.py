def patch_default(function, position, name, new_default):
    def patched(*args, **kwargs):
        print("Getting invoked")
        print(args)
        print(kwargs)

        if len(args) > position:
            args[position] = new_default
        else:
            kwargs[name] = new_default

        print(args)
        print(kwargs)

        return function(*args, **kwargs)

    return patched
