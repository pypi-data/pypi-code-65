#!/usr/bin/env python

import docker
import glob
import json
import hashlib
import os
import tempfile
import types
import typing

from docker_ops import utils as docker_ops_utils, constants as docker_ops_constants

PWN = typing.TypeVar('PWN')

class Version:
    def __init__(self: PWN, version: str) -> None:
        version = version or '0.0.0'
        self._major = int(version.split('.', 1)[0])
        self._minor = int(version.split('.', 2)[1])
        self._minor_minor = int(version.rsplit('.', 1)[1])

    def inc_minor_minor(self: PWN) -> None:
        self._minor_minor = self._minor_minor + 1

    def get_version(self: PWN) -> None:
        return f'{self._major}.{self._minor}.{self._minor_minor}'

    def __repr__(self:PWN) -> str:
        return f'Version[{self.get_version()}]'

class Hash:
    def __init__(self: PWN, dockerfile_path: str, source_paths: typing.List[str] = []) -> str:
        if not os.path.exists(dockerfile_path):
            raise IOError(f'Unable to load Dockerfile[{dockerfile_path}]')

        self._hashes = []
        for source_path in source_paths:
            self._hashes.append(docker_ops_utils.hash_directory(source_path))

        with open(dockerfile_path, 'rb') as stream:
            self._hashes.append(hashlib.sha256(stream.read()).hexdigest())

    def get_hash(self: PWN) -> str:
        hashes = ''.join(self._hashes)
        hashes = hashes.encode('utf-8')
        return hashlib.sha256(hashes).hexdigest()

    def __repr__(self: PWN) -> str:
        return f'Build Hash: {self.get_hash()}'

class Docker:
    def __init__(self: PWN, build_dir: str, dockerfile_path: str, build_name: str, build_variant: str) -> None:
        self._build_dir = build_dir
        self._dockerfile_path = dockerfile_path
        if not os.path.exists(dockerfile_path):
            raise IOError(f'Missing Dockerfile[{dockerfile_path}]')

        rel_dockerfile_path = dockerfile_path.replace(build_dir, '').strip('/')
        if not os.path.exists(os.path.join(build_dir, rel_dockerfile_path)):
            raise IOError(f'Dockefile not found: {rel_dockerfile_path}')

        self._dockerfile_path = rel_dockerfile_path
        self._client = docker.APIClient(base_url='unix://var/run/docker.sock')
        if build_variant:
            self._build_name = f'{build_variant}.{build_name}'.lower().replace('.', '-')

        else:
            self._build_name = build_name.lower().replace('.', '-')

        self._build_name_full = f'{docker_ops_constants.IMAGE_REGISTRY_DOMAIN}/{self._build_name}'

    def _stream_output_dev_null(self: PWN, generator: typing.Any) -> None:
        while True:
            try:
                generator.__next__()
            except StopIteration:
                break

    def _stream_output(self: PWN, generator: typing.Any) -> None:
        while True:
            try:
                output = generator.__next__()
                output = json.loads(output.decode(docker_ops_constants.ENCODING))
                if 'stream' in output.keys():
                    print(output['stream'].strip('\n'))
            except StopIteration:
                break

    def set_latest(self: PWN, version: str) -> None:
        build_name = f'{self._build_name}:{version}'
        self._client.tag(build_name, self._build_name, 'latest')
        self._client.tag(build_name, self._build_name_full, 'latest')

    def build(self: PWN, version: str, verbose: bool = False, tag_latest: bool = True) -> str:
        build_name = f'{self._build_name}:{version}'
        generator = self._client.build(path=self._build_dir, dockerfile=self._dockerfile_path, tag=build_name)
        if verbose:
            self._stream_output(generator)

        else:
            self._stream_output_dev_null(generator)

        self._client.tag(build_name, self._build_name_full, version)
        return build_name

    # Push utility functions
    def _format_push_output(self: PWN, line: typing.Any) -> None:
        if 'id' in line.keys() and 'progress' in line.keys():
            _id = line['id']
            status = line['status']
            progress = line['progress']
            return f'{_id} {status} {progress}'

        elif 'id' in line.keys():
            _id = line['id']
            status = line['status']
            return f'{_id} {status}'

        elif 'aux' in line.keys():
            tag = line['aux']['Tag']
            digest = line['aux']['Digest']
            size = line['aux']['Size']
            return f'{tag} {digest} {size}'

        elif 'status' in line.keys():
            status = line['status']
            return f'Status: {status}'

        elif 'errorDetail' in line.keys():
            raise NotImplementedError(line['errorDetail']['message'])
            import pdb; pdb.set_trace()
            import sys; sys.exit(1)

        else:
            return f'Other: {line}'

    def _stream_push_output__dev_null(self: PWN, generator: types.GeneratorType) -> None:
        while True:
            try:
                generator.__next__()
            except StopIteration:
                break

    def _stream_push_output(self: PWN, generator: types.GeneratorType) -> None:
        while True:
            try:
                next_line = generator.__next__()

            except StopIteration:
                break

            else:
                print(self._format_push_output(next_line))

    def push(self: PWN, version: str, verbose: bool = True) -> str:
        generator = self._client.push(self._build_name_full, version, stream=True, decode=True)
        if verbose:
            self._stream_push_output(generator)

        else:
            self._stream_push_output__dev_null(generator)

        build_name = f'{self._build_name_full}:{version}'
        return build_name

class BuildInfo:
    KEYS = ['version', 'name', 'hash']
    def __init__(self: PWN, build_dir: str, dockerfile_path: str, source_paths: typing.List[str] = []) -> None:
        self._build_dir = build_dir
        self._build_name = os.path.basename(build_dir)
        self._dockerfile_path = dockerfile_path
        self._source_paths = source_paths
        self._build_variant = os.path.basename(dockerfile_path).rsplit('.')[0]
        if self._build_variant == 'Dockerfile':
            self._build_variant = None

        self._build_info_filepath = os.path.join(build_dir, 'build-info.json')
        if not os.path.exists(self._build_info_filepath):
            self._build_info = {
                'name': self._build_name,
            }
            if self._build_variant:
                self._build_info['builds'] = {}

        else:
            with open(self._build_info_filepath, 'rb') as stream:
                build_info = json.loads(stream.read().decode(docker_ops_constants.ENCODING))
                if not 'builds' in build_info.keys() and self._build_variant:
                    build_info['builds'] = {
                            self._build_variant: {
                                'hash': build_info['hash'],
                                'version': build_info['version']
                            }
                        }

                self._build_info = build_info

    @property
    def name(self: PWN) -> str:
        return self._build_info['name']

    @property
    def variant(self: PWN) -> str:
        return self._build_variant

    @property
    def version(self: PWN) -> Version:
        if hasattr(self, '_version'):
            return self._version

        if self._build_info.get('builds', None):
            self._version = self._build_info['builds'].get(self._build_variant, {}).get('version', None)

        else:
            self._version = self._build_info.get('version', None)

        self._version = Version(self._version)
        return self._version

    @property
    def hash(self: PWN) -> Hash:
        if hasattr(self, '_hash'):
            return self._hash

        self._hash = Hash(self._dockerfile_path, self._source_paths)
        return self._hash

    @property
    def docker(self: PWN) -> Docker:
        if hasattr(self, '_docker'):
            return self._docker

        self._docker = Docker(self._build_dir, self._dockerfile_path, self.name, self.variant)
        return self._docker

    def __repr__(self: PWN) -> str:
        if self.variant:
            name = f'{self.variant}.{self.name}'.lower().replace('.', '-')

        else:
            name = f'{self.name}'.lower().replace('.', '-')

        return f'{name} {self.version.get_version()}'

    def new_build_required(self: PWN) -> bool:
        if 'builds' in self._build_info.keys():
            return self._build_info['builds'].get(self._build_variant, {}).get('hash', None) != self.hash.get_hash()

        return self._build_info.get('hash', None) != self.hash.get_hash()

    def store(self: PWN) -> None:
        if self._build_variant is None:
            self._build_info['hash'] = self.hash.get_hash()
            self._build_info['version'] = self.version.get_version()
        else:
            self._build_info['builds'][self._build_variant] = {
                'hash': self.hash.get_hash(),
                'version': self.version.get_version()
            }

        data = json.dumps(self._build_info, indent=2).encode(docker_ops_constants.ENCODING)
        with open(self._build_info_filepath, 'wb') as stream:
            stream.write(data)

def find_build_infos(image_dir: str, source_paths: typing.List[str]) -> types.GeneratorType:
    new_build_infos = []
    for root, dirnames, filenames in os.walk(image_dir):
        for dirname in dirnames:
            if dirname == 'Dockerfiles':
                dirpath = os.path.join(root, dirname)
                build_dir = root
                for dockerfile_path in glob.glob(f'{dirpath}/*.Dockerfile'):
                    filename = os.path.basename(dockerfile_path)
                    image_name = filename.rsplit('.', 1)[0]

                    s_paths = []
                    for source_path in source_paths:
                        full_path = os.path.join(build_dir, source_path)
                        if os.path.exists(full_path):
                            if os.path.isdir(full_path):
                                s_paths.append(full_path)
                            else:
                                s_paths.append(os.path.dirname(full_path))

                    yield BuildInfo(build_dir, dockerfile_path, s_paths)

            else:
                build_dir = os.path.join(root, dirname)
                dockerfile_path = os.path.join(build_dir, 'Dockerfile')
                if not os.path.exists(dockerfile_path):
                    continue

                s_paths = []
                for source_path in source_paths:
                    full_path = os.path.join(build_dir, source_path)
                    if os.path.exists(full_path):
                        if os.path.isdir(full_path):
                            s_paths.append(full_path)
                        else:
                            s_paths.append(os.path.dirname(full_path))

                yield BuildInfo(build_dir, dockerfile_path, s_paths)

def scan_and_build(directory_path: str, source_paths: typing.List[str], verbose: bool=True) -> None:
    infos = []
    for build_info in find_build_infos(directory_path, source_paths):
        if build_info.new_build_required():
            build_info.version.inc_minor_minor()
            build_info.docker.build(build_info.version.get_version(), verbose=True)
            build_info.docker.set_latest(build_info.version.get_version())
            build_info.docker.push(build_info.version.get_version(), verbose=True)
            build_info.docker.push('latest', verbose=True)
            infos.append([True, build_info])

        else:
            infos.append([False, build_info])

        build_info.store()

    if verbose:
        for new_build, info in infos:
            if new_build:
                print(f'New Build[{info}]')

            else:
                print(f'Not Built[{info}]')

