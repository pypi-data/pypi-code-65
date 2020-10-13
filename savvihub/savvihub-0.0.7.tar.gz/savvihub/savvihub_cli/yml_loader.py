from jsonschema import validate, ValidationError

import yaml


class YmlLoader:
    def __init__(self, filename, schema):
        self.filename = filename
        self.schema = schema
        self.data = self._load()
        self._validate()

    def _load(self):
        try:
            with open(self.filename) as f:
                documents = yaml.full_load(f)
                if not documents:
                    return None
                data_dict = dict()
                for item, doc in documents.items():
                    data_dict[item] = doc
                return data_dict
        except EnvironmentError:
            print('Error: Config file not found')

    def _validate(self):
        try:
            validate(instance=self.data, schema=self.schema)
        except ValidationError as e:
            return e.schema["Validation Error"]

    def pop_val_by_key(self, key):
        return self.data.pop(key, None)

    def _is_duplicated(self, key, value):
        if value in self.data[key]:
            return True
        else:
            return False

    def write(self, dict_data):
        try:
            with open(self.filename, 'w') as f:
                yaml.safe_dump(dict_data, f, default_flow_style=False)
        except EnvironmentError:
            print('Error: Config file not found')

    def update_and_write(self, dict_data):
        for k, v in dict_data.items():
            if k in self.data.keys():
                if type(self.data[k]) == list:
                    if self._is_duplicated(k, v):
                        raise Exception('Duplicated value!')
                    self.data[k].append(v)
                else:
                    self.data[k] = v
            else:
                properties = self.schema.get('oneOf')[1].get('properties')
                if k in properties.keys():
                    if properties.get(k).get('type') == 'array':
                        self.data[k] = [v]
                    else:
                        self.data[k] = v
                else:
                    raise Exception('Wrong key: ', k)
        self.write(self.data)

    def is_ready_to_run(self):
        if not self.data.get('data_mount_infos', None):
            return False
        else:
            return True


class ExperimentYmlLoader(YmlLoader):
    schema = {
        "oneOf": [
            {"type": "null"},
            {
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "project": {"type": "string"},
                    "image_id": {"type": "string"},
                    "resource_spec_id": {"type": "string"},
                    "data_mount_infos": {
                        "type": "array",
                        "properties": {
                            "id": {"type": "string"},
                            "ref": {"type": "string"},
                            "mount_path": {"type": "string"}
                        },
                        "required": ["id", "ref", "mount_path"]
                    },
                    "start_command": {"type": "string"}
                },
                "required": ["workspace", "project"]
            }
        ]
    }

    def __init__(self, filename):
        super().__init__(filename, self.schema)
