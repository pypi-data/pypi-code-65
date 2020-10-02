#  Copyright (c) 2020  SBA - MIT License

from setuptools.command.build_py import build_py as _build_py
from distutils.command.build import build as _build
from distutils.cmd import Command
from distutils.log import ERROR, WARN
from distutils.dep_util import newer
import os.path
import glob
import shlex
import subprocess
import tempfile


class build(_build):
    parent = _build

    def run(self):
        if "build_py" in self.distribution.cmdclass:
            p = self.distribution.cmdclass["build_py"]
            if p != build_py:
                build_py.parent = p
        self.distribution.cmdclass["build_py"] = build_py
        self.parent.run(self)


class build_py(_build_py):
    parent = _build_py

    def run(self):
        self.run_command("build_ui")
        self.run_command("build_qm")
        self.run_command("build_rc")
        self.parent.run(self)

    def get_outputs(self):
        build_ui = self.get_finalized_command("build_ui")
        build_qm = self.get_finalized_command("build_qm")
        build_rc = self.get_finalized_command("build_rc")
        return (_build_py.get_outputs(self) + build_ui.get_outputs()
                + build_qm.get_outputs() + build_rc.get_outputs()
                )


class BuildUi(Command):
    description = "\"build\" ui_*.py files from *.ui ones"

    user_options = [
        ('force', 'f', 'rebuild unconditionally'),
        ('uic=', 'u', 'uic compiler (default pyside2-uic')
    ]

    def initialize_options(self):
        self.outputs = []
        self.force = None
        self.uic = None
        self.packages = None

    def finalize_options(self):
        if self.force is None:
            self.force = False
        if self.uic is None:
            self.uic = 'pyside2-uic'
        if self.packages is None:
            self.packages = self.distribution.packages

    def compile(self, file, pyfile):
        p = subprocess.run(self.cmd + [file, '-o', pyfile])
        if p.returncode != 0:
            self.announce('Fatal error in ' + file, level=WARN)

    def run(self):
        self.cmd = shlex.split(self.uic)
        prog = find_exec(self.cmd[0])
        if prog is None:
            self.announce('Could not find "{}", giving up'.format(self.cmd[0]),
                          level=ERROR)
            return
        self.cmd[0] = prog
        self.announce("Build ui - force: {} - uic: {}".format(
            self.force, ' '.join(self.cmd)))
        for p in self.packages:
            for file in glob.glob(os.path.join(p, '**', '*.ui'),
                                  recursive=True):
                d, f = os.path.split(file)
                py_file = os.path.join(d, 'ui_' + f[:-2] + 'py')
                if self.force or newer(file, py_file):
                    self.execute(self.compile, [file, py_file],
                                 'Compiling {} to {}'.format(file, py_file))

    def get_outputs(self):
        return self.outputs


class BuildQm(Command):
    description = "\"build\" *.qm files from *.ts ones (requires lrelease)"

    user_options = [
        ('force', 'f', 'rebuild unconditionally'),
        ('lrelease=', 'l', 'language file compiler (default lrelease')
    ]

    def initialize_options(self):
        self.outputs = []
        self.force = None
        self.lrelease = None
        self.i18n = None

    def finalize_options(self):
        if self.force is None:
            self.force = False
        if self.lrelease is None:
            self.lrelease = 'lrelease'
        if self.i18n is None:
            self.i18n = ['i18n']

    def compile(self, file):
        p = subprocess.run(self.cmd + [file])
        if p.returncode != 0:
            self.announce('Fatal error in ' + file, level=WARN)

    def run(self):
        self.cmd = shlex.split(self.lrelease)
        prog = find_exec(self.cmd[0])
        if prog is None:
            self.announce('Could not find "{}", giving up'.format(self.cmd[0]),
                          level=ERROR)
            return
        self.cmd[0] = prog
        self.announce("Build qm - force: {} - lrelease: {}".format(
            self.force, ' '.join(self.cmd)))
        for p in self.i18n:
            for file in glob.glob(os.path.join(p, '**', '*.ts'),
                                  recursive=True):
                qm_file = file[:-2] + 'qm'
                if self.force or newer(file, qm_file):
                    self.execute(self.compile, [file],
                                 'Compiling {} to {}'.format(file, qm_file))

    def get_outputs(self):
        return self.outputs


class BuildRc(Command):
    description = "\"build\" a resource.py file from *.qm ones and icon"

    user_options = [
        ('force', 'f', 'rebuild unconditionally'),
        ('rcc=', 'l', 'resource compiler (default pyside2-rcc')
    ]

    def initialize_options(self):
        self.outputs = []
        self.force = None
        self.rcc = None
        self.i18n = None
        self.packages = None
        self.rcfile = None

    def finalize_options(self):
        name = self.distribution.get_name()
        if self.force is None:
            self.force = False
        if self.rcc is None:
            self.rcc = 'pyside2-rcc'
        if self.i18n is None:
            self.i18n = ['i18n']
        if self.packages is None:
            self.packages = self.distribution.packages
        if self.rcfile is None:
            if name in self.packages or len(self.packages) == 0:
                rcdir = name
            else:
                rcdir = self.packages[0]
            self.rcfile = os.path.join(rcdir, 'resource.py')

    def compile(self, files, icon=None):
        with tempfile.TemporaryDirectory() as d:
            qrc = os.path.join(d, 'resource.qrc')
            with open(qrc, 'w') as out:
                out.write('<!DOCTYPE RCC>\n<RCC version="1.0">\n  <qresource prefix="/lang">\n')
                for file in files:
                    name = os.path.basename(file)
                    splitted = name.rsplit('.', 1)[0].split('_', 1)
                    if len(splitted) == 2: name = splitted[1]
                    out.write('    <file alias="{}">{}</file>\n'
                              .format(name, os.path.abspath(file)))
                if icon is not None:
                    out.write('  </qresource>\n  <qresource prefix="/icon">\n')
                    out.write('    <file alias="app.ico">{}</file>\n'.format(icon))
                out.write('  </qresource>\n</RCC>\n')

            p = subprocess.run(self.cmd + [qrc, '-o', self.rcfile])
            if p.returncode != 0:
                self.announce('Fatal error building ' + self.rcfile, level=WARN)

    def run(self):
        self.run_command("build_qm")
        self.cmd = shlex.split(self.rcc)
        prog = find_exec(self.cmd[0])
        if prog is None:
            self.announce('Could not find "{}", giving up'.format(self.cmd[0]),
                          level=ERROR)
            return
        self.cmd[0] = prog
        self.announce("Build rc - force: {} - rcc: {}".format(
            self.force, ' '.join(self.cmd)))
        files = []
        args = [files]
        process = False
        for p in self.i18n:
            for file in glob.glob(os.path.join(p, '**', '*.qm'),
                                  recursive=True):
                files.append(file)
                if not process and newer(file, self.rcfile):
                    process = True
        if os.path.exists('resources/qtimgren.ico'):
            args.append(os.path.abspath('resources/qtimgren.ico'))
        if process or self.force:
            if len(files) == 0:
                self.announce("No qm files found", level=WARN)
            else:
                self.execute(self.compile, args,
                             'Building {}'.format(self.rcfile))

    def get_outputs(self):
        return self.outputs


def find_exec_builder():
    import shutil

    path = os.environ.get('PATH', os.defpath)
    try:
        from PySide2.QtCore import QLibraryInfo as Info

        libex = Info.location(Info.LibraryExecutablesPath)
        if libex not in path.split(os.pathsep):
            path += os.pathsep + libex
    except ImportError:
        pass
    return lambda prog: shutil.which(prog, path=path)


find_exec = find_exec_builder()
