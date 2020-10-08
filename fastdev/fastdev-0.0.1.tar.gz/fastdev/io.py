import pickle
import json

def load_jsonlines(filepath):
    with open(filepath, 'r') as reader:
        return list(map(json.loads, reader))

def load_pickle(filepath):
    with open(filepath, 'rb') as reader:
        return pickle.load(reader)

def save_pickle(data, filepath):
    with open(filepath, 'wb') as writer:
        pickle.dump(data, writer)

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as reader:
        return json.load(reader)

def save_json(data, filepath, not_chinese=True):
    with open(filepath, 'w', encoding='utf-8') as writer:
        json.dump(data, writer, ensure_ascii=not_chinese)

def load_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as reader:
        return [line for line in reader if line.strip()]

def save_txt(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as writer:
        writer.write('\n'.join(data))

def pretty_json(var):
    print(json.dumps(var, indent=4))