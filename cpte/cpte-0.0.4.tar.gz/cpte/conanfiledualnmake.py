from conans import AutoToolsBuildEnvironment, tools
from .conanfileautotools import ConanFileAutoTools
import os


class ConanFileDualNMake(ConanFileAutoTools):
    _msvc_project = None
    _msvc_folder = None

    def build(self):
        if self._is_msvc:
            msvc_path = os.path.join(self._source_subfolder, self._msvc_folder)
            with tools.chdir(msvc_path):
                with tools.vcvars(self.settings, force=True):
                    self.run('nmake -f {} CFG={}'.format(self._msvc_project, self.settings.build_type))
        else:
            ConanFileAutoTools.build(self)

    def package(self):
        if self._is_msvc:
            msvc_path = os.path.join(self._source_subfolder, self._msvc_folder)
            with tools.chdir(msvc_path):
                self.run('nmake -f Makefile.vc prefix="%s" install' % os.path.abspath(self.package_folder))
        else:
            ConanFileAutoTools.package(self)
