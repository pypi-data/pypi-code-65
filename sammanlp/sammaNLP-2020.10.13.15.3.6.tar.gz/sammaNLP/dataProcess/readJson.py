
import json
import os


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f1:
        json_content = json.load(f1)
        return json_content


def read_json_fold(fold_path):
    for file_name in os.listdir(fold_path):
        file_path = '{}\\{}'.format(fold_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f1:
            json_content = json.load(f1)
            yield json_content
