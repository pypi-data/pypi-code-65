from conans import MSBuild, tools
from .conanfileautotools import ConanFileMeson
import os


class ConanFileVS(ConanFileMeson):
    _msvc_project = None
    _msvc_folder = None

    def _configure_builder(self):
        if self._builder:
            return self._builder

        self._builder = MSBuild(self)

        return self._builder

    def build(self):
        builder = self._configure_builder()
        project_foler = os.path.join(self.build_folder, self._source_subfolder, self._msvc_folder)
        with tools.chdir(project_foler):
            builder.build(self._msvc_project, build_type=self.settings.build_type)

    def package(self):
        self.copy('COPYING', src=self._source_subfolder, dst='licenses')
        self.copy("license*", src=self._source_subfolder, dst='licenses')
        self.copy('*.exe', src=os.path.join(self._source_subfolder),
                  dst=os.path.join(self.package_folder, 'bin'), keep_path=False)
        self.copy('*.dll', src=os.path.join(self._source_subfolder),
                  dst=os.path.join(self.package_folder, 'bin'), keep_path=False)
        self.copy('*.lib', src=os.path.join(self._source_subfolder),
                  dst=os.path.join(self.package_folder, 'lib'), keep_path=False)
        self.copy('*.h', src=os.path.join(self._source_subfolder, 'gstreamer', 'gstreamermm'),
                  dst=os.path.join(self.package_folder, 'include'), keep_path=True)
