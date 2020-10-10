from conans import CMake
from .conanfilemeson import ConanFileMeson


class ConanFileCMake(ConanFileMeson):
    def _configure_builder(self):
        if self._builder:
            return self._builder

        self._builder = CMake(self)
        self._builder.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)

        return self._builder

    def package(self):
        self.copy('COPYING', src=self._source_subfolder, dst='licenses')
        builder = self._configure_builder()
        builder.install()
