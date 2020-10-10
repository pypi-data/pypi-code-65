import yaml


class ObjectDict:
    """Generate dictionary representation of object arguments"""
    def __init__(self, _object: object):
        self._object = _object

    def get_attrs(self):
        return self._object.__dict__


class YamlDump:
    def __init__(self, object_dict: dict):
        self.object_dict = object_dict

    def generate_yaml(self):
        """Generate yaml string from object_dict"""
        myyaml = yaml.dump(self.object_dict)
        myyaml = myyaml[myyaml.find("\n")+2:]
        return myyaml

    def write_file(self, outfile: str):
        with open(outfile, "w") as file:
            return file.write(self.generate_yaml())


class Serialize:
    def __init__(self, object_to_serialize):
        self.object_to_serialize = object_to_serialize
        self.object_dict = ObjectDict(object_to_serialize)

    def generate_name(self, name: str = False):
        if name is False:
            return self.object_to_serialize.__class__.__name__ + ".yml"
        else:
            return name

    def write(self, name: str = False):
        yaml_dump = YamlDump(self.object_dict)
        name = self.generate_name(name)
        return yaml_dump.write_file(name)

    def get(self):
        yaml_dump = YamlDump(self.object_dict)
        serialized_yaml = yaml_dump.generate_yaml()
        return serialized_yaml
