import json

"""
("tuple", [("float", None), ("record", OrderedDict(a=("float", None)))])
"""


def serialize_list(x, schema):
    f = dispatch[schema[0]]
    return "[{}]".format(",".join([f(y, schema[1]) for y in x]))


def serialize_tuple(x, schema):
    elements = []
    for (t, e) in zip(schema, x):
        f = dispatch[t[0]]
        elements.append(f(e, t[1]))
    return "[{}]".format(",".join(elements))


def serialize_record(x, schema):
    entries = []
    for (k, t) in schema.items():
        f = dispatch[t[0]]
        entries.append("{}={}".format(k, f(x[k], t[1])))
    return "{{{}}}".format(",".join(entries))


def serialize_float(x, schema):
    return str(x)


def serialize_int(x, schema):
    return str(x)


def serialize_str(x, schema):
    return '"{}"'.format(x)


def serialize_bool(x, schema):
    if x:
        return "true"
    else:
        return "false"


dispatch = dict(
    list=serialize_list,
    tuple=serialize_tuple,
    record=serialize_record,
    float=serialize_float,
    int=serialize_int,
    str=serialize_str,
    bool=serialize_bool,
)


def mlc_serialize(x, schema):
    return dispatch[schema[0]](x, schema[1])


def mlc_deserialize(x, t):
    return json.loads(x)
