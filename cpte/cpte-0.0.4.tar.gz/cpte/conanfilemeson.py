from conans import ConanFile, Meson, tools
import os
import glob
import shutil


class ConanFileMeson(ConanFile):
    url = 'https://github.com/fluendo/fluendo-conan'
    author = 'Fluendo'
    generators = ('cmake', 'pkg_config')

    _builder = None
    _git_url = None
    _git_branch = None
    _defs = dict()
    _args = None
    _requires = []
    _build_requires = []
    _use_sudo = False
    _meson_backend = 'Ninja'

    @property
    def _source_subfolder(self):
        return 'source_subfolder'

    @property
    def _build_subfolder(self):
        return 'build_subfolder'

    @property
    def _is_mingw(self):
        return tools.os_info.is_windows and self.settings.compiler == 'gcc'

    @property
    def _is_msvc(self):
        return tools.os_info.is_windows and self.settings.compiler == 'Visual Studio'

    def _configure_builder(self):
        if self._builder:
            return self._builder
        self._builder = Meson(self, backend=_meson_backend)
        self._builder.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder,
                                defs=self._defs, args=self._args)
        return self._builder

    def copy_pkg_config(self, name):
        root = self.deps_cpp_info[name].rootpath
        pc_dir = os.path.join(root, 'lib', 'pkgconfig')
        pc_files = glob.glob('{}/*.pc'.format(pc_dir))
        self.output.warn('Copy .pc files to {}'.format(os.getcwd()))
        if not pc_files:  # maybe it's stored in .pc at root
            pc_files = glob.glob('{}/*.pc' % root)
        for pc_name in pc_files:
            new_pc = os.path.basename(pc_name)
            self.output.warn('\tcopy {}'.format(os.path.basename(pc_name)))
            shutil.copy(pc_name, new_pc)
            if tools.os_info.is_windows:
                prefix = root.replace('\\', '/')
            else:
                prefix = root
            tools.replace_prefix_in_pc_file(new_pc, prefix)

    def _get_path_from_deps(self, dependencies):
        path = ''
        for dependency in dependencies:
            path += self._get_path_from_vector(
                dependencies[dependency], self.deps_cpp_info[dependency].rootpath)
        return path

    def _get_path_from_vector(self, paths, root_path):
        path = ''
        for items in paths:
            tmp_path = os.path.join(root_path)
            for item in items:
                tmp_path = os.path.join(tmp_path, item)
            path += tmp_path + os.pathsep
        return path

    def _get_path_from_conanfile(self, paths):
        return self._get_path_from_vector(paths, os.getcwd())

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def environment_append(self, variable_name, variable_value):
        tmp_value = variable_value
        if variable_name in os.environ:
            tmp_value += os.environ[variable_name]
        return tmp_value

    def environment_append_dict(self, environment_variables):
        for name_var in environment_variables:
            if name_var in os.environ:
                if environment_variables[name_var]:
                    environment_variables[name_var] = os.environ[name_var] + os.pathsep + environment_variables[
                        name_var]
                else:
                    environment_variables[name_var] = os.environ[name_var]
            else:
                environment_variables[name_var] = environment_variables[name_var]
        return environment_variables

    def requirements(self):
        for require in self._requires:
            self.requires(require)

    def build_requirements(self):
        for build_require in self._build_requires:
            self.build_requires(build_require)

    def source(self):
        if not self._git_branch:
            self._git_branch = self.version
        git = tools.Git(folder=self._source_subfolder)
        git.clone(self._git_url, self._git_branch)

    def build(self):
        builder = self._configure_builder()
        builder.build()

    def package(self):
        self.copy('COPYING', src=self._source_subfolder, dst='licenses')
        self.copy(pattern='LICENSE', src=self._source_subfolder, dst='licenses')
        builder = self._configure_builder()
        builder.install()
