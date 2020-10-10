import json
import io
import os
import subprocess

def read_json_file(file_path):
    with open(file_path) as json_data:
        d = json.load(json_data)
        return d
def write_json_file(data, file_path):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    with io.open(file_path, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data, indent=2, 
                          sort_keys=False,
                          separators=(',', ': '), 
                          ensure_ascii=False)
        outfile.write(to_unicode(str_))
    return

def git_commit(static_path, message, files = "."):
    current_path = os.getcwd()
    os.chdir(static_path)
    subprocess.run(["git", "add", files])
    subprocess.run(["git", "commit", "-m", message])
    os.chdir(current_path)

def yes_no(answer):
    yes = set(['yes', 'y', 'ye', ''])
    no = set(['no', 'n'])

    while True:
        choice = input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'\n")

def bump_version(file_path, position):
  package_json = read_json_file(file_path)
  version = package_json["version"]
  name = package_json["name"]
  arr = version.split(".")
  arr[position] = str(int(arr[position]) + 1)
  new_version = ".".join(arr)
  package_json["version"] = new_version
  write_json_file(package_json, file_path)
  return name, new_version

def bump_major(file_path):
    return bump_version(file_path, 0)
def bump_minor(file_path):
    return bump_version(file_path, 1)
def bump_path(file_path):
    return bump_version(file_path, 2)
