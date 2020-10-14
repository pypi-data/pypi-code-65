import yaml


def load_from_yaml(yaml_file, key=None):
    with open(yaml_file, 'rb') as fr:
        yaml_content = yaml.safe_load(fr)
    if key is None:
        return yaml_content
    return yaml_content[key]
