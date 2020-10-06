def set_nested_dictionary(d_, root, one, two=None):
    # In the form Dictionary[LIMS #][Identifier (e.g., FTIR or "Technique")] = {Set Data}

    m_two = set(two) if two else set()

    try:
        d_[root][one].add(two)
    except KeyError:
        try:
            d_[root].update({one: m_two})
        except KeyError:
            d_[root] = {one: m_two}
        except TypeError:
            d_[root].update({one: set()})


def deep(*args, d=None):
    root = args[0]
    if not d:
        d = {}
    if isinstance(args, tuple):
        args = [data for data in args]
    depth = len(args)
    for arg in args[1:]:
        print(arg)
        print(d)
        d[root] = {arg, deep(args[1:], d)}
    return d
