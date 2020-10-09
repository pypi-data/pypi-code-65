import sys
import argparse
import subprocess
import tempfile
import os
import json
from .common.utils import *
from .common.globals import *


def parse_args():
    parser = argparse.ArgumentParser(description='upload a package and ALL its dependencies to a remote server')
    parser.add_argument('reference',
                        metavar='reference',
                        type=str,
                        help='conanfile dir or reference')

    parser.add_argument('--profile', '-pr',
                        type=str,
                        metavar='profile',
                        help="Apply the specified profile to the install command")
    parser.add_argument('--remote', '-r',
                        type=str,
                        metavar='remote',
                        help="conan remote for upload",
                        required=True)

    parser.add_argument('--options', '-o',
                        type=str,
                        metavar='PROFILE',
                        nargs="+",
                        help="cDefine options values, e.g., -o Pkg:with_qt=True")
    parser.add_argument('--env', '-e',
                        type=str,
                        metavar='e',
                        nargs="+",
                        help="co for upload")

    parser.add_argument('--settings', '-s',
                        type=str,
                        metavar='SETTINGS',
                        nargs="+",
                        help="Settings to build the package, overwriting the defaults. e.g., -s compiler=gcc")

    parser.add_argument('--check',
                        action='store_true',
                        help="perform an integrity check, using the manifests,before upload ")

    parser.add_argument('--all',
                        action='store_true',
                        help="Upload both package recipe and packages")

    parser.add_argument('--skip-upload',
                        action='store_true',
                        help="Upload both package recipe and packages")

    parser.add_argument('--confirm', '-c',
                        action='store_true',
                        help="Upload all matching recipes without confirmation")

    parser.add_argument('--dry-run',
                        action='store_true',
                        help="Do not upload, only show what would be done")
    parser.add_argument('--parallel',
                        action='store_true',
                        help="Upload files in parallel using multiple "
                             "threads the default number of launched threads is 8")

    parser.add_argument('--retry',
                        type=int,
                        metavar="RETRY",
                        help="In case of fail retries to upload again the specified times.")

    parser.add_argument('--retry-wait',
                        type=int,
                        metavar="SEC",
                        help="Waits specified seconds before retry again")

    parser.add_argument('-no', '--no-overwrite',
                        type=str,
                        metavar="{all, recipe}",
                        help="Uploads package only if recipe is the same as the remote one")

    return parser.parse_args()


def get_packages(json_data):
    output = []
    error = False
    for p in json_data:
        _ref = None
        _id = None
        _binary = None
        _recipe = None
        _is_ref = False
        try:
            _is_ref = p['is_ref']
        except KeyError:
            pass

        try:
            _ref = p['reference']
        except KeyError:
            pass

        try:
            _id = p['id']
        except KeyError:
            pass

        try:
            _binary = p['binary']
        except KeyError:
            pass

        try:
            _recipe = p['recipe']
        except KeyError:
            pass

        if not _is_ref:
            continue

        if _ref == None or _ref == "" or _id == None or _id == "":
            print("ERROR: parsing error of json content")
            print(_ref, _id, _binary, _recipe)
            error=True
        
        if ( _binary != "Cache" or _recipe != "Cache" ):
            print("ERROR: can not upload package %s:%s : package does not exist" % (_ref, _id))
            error=True

        output.append((_ref,_id,_binary, _recipe ))

        
    if error:
        print("exiting due to previous errors.")
        exit(1)
    
    return output


def upload_packages(packages, args):
    upload_cmd = [conan_exe, 'upload']

    if args.all:
        upload_cmd += ['--all']

    if args.skip_upload:
        upload_cmd += ['--skip-upload']

    if args.confirm:
        upload_cmd += ['--confirm']

    if args.parallel:
        upload_cmd += ['--parallel']
    
    if args.retry:
        upload_cmd += ['--retry', args.retry]

    if args.retry_wait:
        upload_cmd += ['--retry-wait', args.retry_wait]

    if args.no_overwrite:
        upload_cmd += ['--no-overwrite', args.no_overwrite]
    
    if args.remote:
        upload_cmd += ['--remote', args.remote]

    
    for i in packages:
        cmd = upload_cmd + [ i[0] + ":" + i[1] ]
        print("uploading package %s:%s binary %s, recipe: %s" % i)

        if not args.dry_run:
            subprocess.check_call(cmd)


if __name__ == "__main__":
    check_python3()
    args = parse_args()

    json_file = tempfile.mkstemp()[1]

    info_command = [conan_exe, 'info', args.reference, '-j', json_file]
    if args.profile:
        info_command += ['-pr', args.profile]

    if args.options:
        for i in args.options:
            info_command += ['-o', i]

    if args.settings:
        for i in args.settings:
            info_command += ['-s', i]

    if args.env:
        for i in args.env:
            info_command += ['-e', i]

    subprocess.check_call(info_command)

    with open(json_file,'rb') as f:
        jsonData = json.load(f)

    upload_packages(get_packages(jsonData), args)
    os.remove(json_file)

    