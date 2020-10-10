import platform
import os
import sys
import yaml

from cpt.packager import ConanMultiPackager
from conans.util.files import load
from conans.errors import ConanException
from conans import tools


def _get_distro_linux():
    distro_info = None
    if sys.version_info >= (3, 8, 0):
        import distro
        distro_info = distro.linux_distribution()
    else:
        import platform
        distro_info = platform.linux_distribution()
    return distro_info


def _get_yaml_name(basename):
    file_basename = os.path.join(os.getcwd(), '{}.yml'.format(basename))
    os_basename = os.path.join(os.getcwd(), '{}_{}.yml'.format(basename, platform.system()))

    if platform.system() == 'Windows':
        if os.path.exists(os_basename):
            return os_basename

    if platform.system() == 'Linux':
        distro_info = _get_distro_linux()
        distro_basename = os.path.join(os.getcwd(), '{}_{}.yml'.format(basename, distro_info[2]))
        if os.path.exists(distro_basename):
            return distro_basename
        if os.path.exists(os_basename):
            return os_basename

    return file_basename


def _load_yaml(data_path):
    if not os.path.exists(data_path):
        return None
    try:
        data = yaml.safe_load(load(data_path))
    except Exception as e:
        raise ConanException('Invalid yml format at {}: {}'.format(data_path, e))

    return data or {}


def _load_tools(tools_info):
    for item in tools_info:
        file_path = os.path.join(tools_info[item]['destination'], item)
        os.environ['PATH'] += os.pathsep + os.path.join(tools_info[item]['destination'])
        if not os.path.exists(file_path):
            tools.get(**(tools_info.get(item)))


class Builder(object):
    _config_data = None
    _shared_settings = None
    _remote = None
    _remote_user = None
    _remote_password = None

    def __init__(self, file_basename):
        data_path = _get_yaml_name(file_basename)
        self._config_data = _load_yaml(data_path)
        if not self._config_data:
            raise ConanException('Invalid yml format at {}, don''t exists '.format(data_path))
        self._shared_settings = self._config_data['shared_setting'][platform.system()]
        print('Loading the {} configuration file '.format(data_path))

    def system(self):
        return platform.system()

    def set_remote(self, remote, remote_user, remote_password):
        self._remote = remote
        self._remote_user = remote_user
        self._remote_password = remote_password

    def run(self):
        if platform.system() == 'Windows' and 'windows_tools' in self._config_data:
            tools_section = self._config_data['windows_tools']
            if tools_section:
                _load_tools(tools_section)
        packages_section = self._config_data['packages']
        if packages_section:
            self.build_packages(packages_section)

    def build_packages(self, packages_section):
        for item in packages_section:
            self.build_package(packages_section[item])

    def build_package(self, package_section):
        settings = self._shared_settings['settings']['settings']
        options = {}
        env_vars = {}
        build = package_section['package']
        build_requires = {}
        local_build_type = []

        if 'options' in package_section:
            options = package_section['options']
        else:
            if 'options' in self._shared_settings:
                options = self._shared_settings['options']

        if 'env_vars' in self._shared_settings:
            env_vars = self._shared_settings['env_vars']

        if 'build_requires' in package_section:
            build_requires = package_section['build_requires']

        if 'os' in package_section:
            if platform.system() not in package_section['os']:
                print('The {} package is not building for the {} platform'.format(
                    build['reference'], platform.system()))
                return

        if 'settings' in package_section and 'build_type' in package_section['settings']:
            local_build_type = package_section['settings']['build_type']

        for env_var in env_vars:
            os.environ[env_var] = env_vars[env_var]

        packager = ConanMultiPackager(**build, build_policy='outdated',
                                      login_username=self._remote_user,
                                      password=self._remote_password,
                                      upload=self._remote)

        for build_type in self._shared_settings['settings']['build_type']:
            if len(local_build_type) == 0 or build_type in local_build_type:
                settings['build_type'] = build_type
                packager.add(settings.copy(), options=options, build_requires=build_requires)

        packager.run()
