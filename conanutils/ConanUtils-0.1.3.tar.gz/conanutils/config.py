#!/usr/bin/env python3


import os
import sys
import subprocess
import json
import re
import argparse
import pkg_resources
import logging

from .common.utils import *
from .common.globals import *


def parse_args():
    parser = argparse.ArgumentParser(
        description='installer for conan configuration')

    parser.add_argument('--new',
                        action="store_true",
                        help="create new config from template")

    parser.add_argument('config',
                        type=str,
                        metavar="CONFIGFILE",
                        help="path to config file")
    return parser.parse_args()


def get_conan_version(conan_exe):
    version_str = subprocess.check_output([conan_exe, "--version"])
    version_str = str(version_str, encoding="ANSI")
    m = re.match(".*([0-9]+\.[0-9]+\.[0-9]+).*", version_str)

    if m:
        return m.group(1)
    else:
        return None


def is_existing_remote(conan_user_path, remote_url):
    json_path = os.path.join(conan_user_path, "remotes.json")
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    remotes = json_data["remotes"]

    for remote in remotes:
        if remote["url"] == remote_url:
            return True

    return False


def add_remote(conan_exe, json_data):
    remotes = json_data["remotes"]
    for remote in remotes.items():

        if (is_existing_remote(conan_user_path, remote[1]["url"])):
            print("remote %s already existing" % (remote[1]["url"]))
            continue

        print("add %s (url: %s)" % (remote[0], remote[1]["url"]))

        user = remote[1].get("user",None)
        passwd = remote[1].get("pass",None)
        
        subprocess.check_call(["conan", "remote", "add", "-i", "0", remote[0], remote[1]["url"]])
        if user is not None and passwd is not None:
            subprocess.check_call(["conan", "user", "-r", remote[0], remote[1]["user"], "-p", remote[1]["pass"]])
        else:
            subprocess.check_call(["conan", "user", "-r", remote[0], "-s"])


def write_settings(p_file, settings):
    for i in settings.items():
        if type(i[1]) == str and " " in i[1]:
            # str_val = '"%s"' % ( i[1] )
            str_val = i[1]
        else:
            str_val = str(i[1])
        line = i[0] + "=" + str_val + "\n"
        p_file.write(line)


def create_conan_profiles(conan_user_path, config):
    profiles_path = os.path.join(conan_user_path, "profiles")
    if not os.path.isdir(profiles_path):
        os.makedirs(profiles_path)

    profiles = config["profiles"]

    for profile in profiles.items():
        print("create profile", profile[0])
        profile_path = os.path.join(profiles_path, profile[0])

        with open(profile_path, 'w') as p_file:
            settings = profile[1]["settings"]
            options = profile[1]["options"]
            env = profile[1]["env"]

            if (settings == None): settings = {}
            if (options == None): options = {}
            if (env == None): env = {}

            build_requires = profile[1]["build_requires"]

            p_file.write("[settings]\n")
            write_settings(p_file, settings)

            p_file.write("[options]\n")
            write_settings(p_file, options)

            p_file.write("[env]\n")
            write_settings(p_file, env)

            p_file.write("[build_requires]\n")
            p_file.write(",\n".join(build_requires))


def get_conan():
    return conan_exe


def pip_exec(json_data, pip_args):
    args = [python_exe, "-m", "pip"] + pip_args + json_data["python_pip_args"]
    print("executing command: \"{}\"".format(" ".join(args)))
    subprocess.check_call(args)


def run_conan_install(json_data):
    conan_target_version = json_data["conan_version"]
    if conan_target_version == "":
        conan_install_string = "conan"
    else:
        conan_install_string = "conan==%s" % conan_target_version

    if not conan_works(conan_exe):
        print("Installing conan package manager...")
        pip_exec(json_data, ["install", conan_install_string])

        if not conan_works(conan_exe):
            raise RuntimeError("failed to install conan")

    elif (conan_target_version != "") and (not get_conan_version(conan_exe) == conan_target_version):
        print("upgrading conan package manager to version %s..." % conan_target_version)
        pip_exec(json_data, ["install", "--upgrade", conan_install_string])


def load_config_json(working_dir):
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = os.path.join(working_dir, 'conan_config.json')

    if not os.path.isfile(json_file):
        raise FileNotFoundError("Json Configuration %s does not exist!" % json_file)

    with open(json_file) as json_file_handle:
        json_data = json.load(json_file_handle)

    return json_data


def main():
    check_python3()
    compute_globals()
    args = parse_args()

    if args.new:
        print("creating new config from template")
        template_file = pkg_resources.resource_filename("conanutils", "/templates/install_config.json.template")

        with open(template_file, 'r') as fin:
            with open(args.config, 'w+') as f:
                f.write(fin.read())

        exit(0)
    else:
        working_dir = os.path.dirname(sys.argv[0])
        json_data = load_config_json(working_dir)

        run_conan_install(json_data)

        create_conan_profiles(conan_user_path, json_data)

        add_remote(conan_exe, json_data)


if __name__ == "__main__":
    main()
