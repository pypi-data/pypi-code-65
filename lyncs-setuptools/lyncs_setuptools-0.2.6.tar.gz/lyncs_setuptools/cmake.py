"""
Tools for running CMake in setup phase
"""

__all__ = [
    "CMakeExtension",
    "CMakeBuild",
]

import os
import subprocess
from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    "Setup extension for CMake"

    def __init__(self, name, source_dir=".", cmake_args=None, post_build=None):
        source_dir = source_dir or "."

        sources = [source_dir + "/CMakeLists.txt"]
        if os.path.exists(source_dir + "/patches"):
            for filename in os.listdir(source_dir + "/patches"):
                sources += [source_dir + "/patches/" + filename]

        Extension.__init__(self, name, sources=sources)
        self.source_dir = os.path.abspath(source_dir)
        self.cmake_args = (
            [cmake_args] if isinstance(cmake_args, str) else (cmake_args or [])
        )
        self.post_build = post_build


class CMakeBuild(build_ext):
    "Build phase of the CMakeExtension"

    def run(self):
        "build_ext function that manages the installation"
        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_extension(ext)
                self.extensions.remove(ext)
        if self.extensions:
            build_ext.run(self)

    def get_install_dir(self, ext):
        "Returns the installation directory (the module base directory)"
        return os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

    def build_extension(self, ext):
        "Runs the CMake scripts in the build phase"

        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError as err:
            raise OSError(
                "CMake must be installed to build the following extensions: " + ext.name
            ) from err

        cmake_args = ["-DEXTERNAL_INSTALL_LOCATION=" + self.get_install_dir(ext)]
        cmake_args += ext.cmake_args

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
        build_args += ["--", "-j", str(abs(os.cpu_count() - 1) or 1)]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        out = subprocess.check_output(
            ["cmake", ext.source_dir] + cmake_args, cwd=self.build_temp, env=env
        )
        out += subprocess.check_output(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )
        print(out)

        if ext.post_build:
            ext.post_build(self, ext)
