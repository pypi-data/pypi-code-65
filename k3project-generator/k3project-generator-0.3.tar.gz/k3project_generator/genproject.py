'''
This module provides the create_reference_project method through which a reference python project can be set up.
'''

import os
import logging
import shutil
import re
from os.path import join, abspath, dirname
from datetime import datetime

RESOURCE_DIR = abspath(join(dirname(__file__), "resources"))

GPLv3 = "GPLv3"
APACHE_2_0 = "APACHE_2_0"
MIT = "MIT"
NO_LICENCE = None

LICENSES = [GPLv3, APACHE_2_0, MIT]

logger = logging.getLogger(__name__)

def _replace_in_file(filePath, searchString, replaceString):
    newlines = []
    with open(filePath,'r') as f:
        for line in f.readlines():
            newlines.append(line.replace(searchString, replaceString))
    with open(filePath, 'w') as f:
        for line in newlines:
            f.write(line)



def _mkdir(dirP):
    logger.debug(f"Creating dir {dirP}")
    os.mkdir(dirP)


def _copyfile(src, dst):
    logger.debug("Copying file to {}".format(dst))
    shutil.copyfile(src, dst)


def _apply_licence(targetDirectory, selectedLicense=None):
    if not selectedLicense:
        return
    if selectedLicense not in LICENSES:
        raise ValueError(f"Invalid licence {selectedLicense}")
    if selectedLicense == APACHE_2_0:
        _copyfile(join(RESOURCE_DIR, "licences",  selectedLicense+"_NOTICE.txt"), join(targetDirectory, "NOTICE"))
        _replace_in_file(join(targetDirectory, "NOTICE"), "{year}", str(datetime.now().year))
    elif selectedLicense == GPLv3:
        licMsg = "GPLv3 was selected as licence. Please follow the instructions within the end of the licence file for each new source file"
        logger.info(licMsg)
        print(licMsg)

    _copyfile(join(RESOURCE_DIR, "licences",  selectedLicense+".txt"), join(targetDirectory, "LICENSE"))
    _replace_in_file(join(targetDirectory, "LICENSE"), "{year}", str(datetime.now().year))
    

def _create_file(filePath, lines=[]):
    logger.debug(f"Creating file {filePath}")
    with open(filePath, 'w') as fh:
        for l in lines:
            fh.write(l+"\n")
        fh.write("\n")

def create_reference_project(targetDirectory, projectName, selectedLicense=None, createDoc=True, createTest=True) -> None:
    '''
    Create a reference project within the given directory
    
    :param targetDirectory: the project directory within in which the project will be created
    :param projectName: the name of the project. Valid characters are a-z, 0-9, - and _ 
    :param selectedLicense: the selected license
    :type selectedLicense: string or None
    '''
    if not re.match("^[a-z0-9_-]+$", projectName):
        raise ValueError("Invalid project name. Project names need to be all lower case characters & numbers and may contain an underscore or hyphen")
    
    if not os.path.isdir(targetDirectory):
        raise NotADirectoryError("Target directory does not exit or is not a directory")
    
    projRoot =  targetDirectory # join(targetDirectory, projectName)
    docDir = join(projRoot, "docs")
    testDir = join(projRoot, "tests")
    rootPackage =  projectName.replace("-","_")
    rootPackageDir = join(projRoot, rootPackage)
    mainPackageDir = join(rootPackageDir, "main")
    
    _apply_licence(projRoot, selectedLicense)
    _copyfile(join(RESOURCE_DIR, "dummy_setup.py"), join(projRoot, "setup.py"))
    _replace_in_file(join(projRoot, "setup.py"), "placeholderproj_root", rootPackage)
    _replace_in_file(join(projRoot, "setup.py"), "placeholderprojnm", projectName)
    
    if createDoc:
        _mkdir(docDir)
    
    _mkdir(rootPackageDir)
    _create_file(join(rootPackageDir, "__init__.py"), [f"from {rootPackage}.alibrary import do_something",
                                                       f"from {rootPackage}._version import __version__"])
    _copyfile(join(RESOURCE_DIR, "dummy_lib.py"), join(rootPackageDir, "alibrary.py"))
    _copyfile(join(RESOURCE_DIR, "dummy__version.py"), join(rootPackageDir, "_version.py"))
    
    
    _mkdir(mainPackageDir)
    _copyfile(join(RESOURCE_DIR, "main__init__.py"), join(mainPackageDir, "__init__.py"))
    
    _copyfile(join(RESOURCE_DIR, "dummy_main.py"), join(mainPackageDir, "cli.py"))
    _replace_in_file(join(mainPackageDir, "cli.py"), "placeholderlib", rootPackage)
    
    if createTest:
        _mkdir(testDir)
        _copyfile(join(RESOURCE_DIR, "dummy_test_.py"), join(testDir, f"test_{rootPackage}.py"))
        _replace_in_file(join(testDir, f"test_{rootPackage}.py"), "placeholderlib", rootPackage)
        _copyfile(join(RESOURCE_DIR, "dummy_test_readme.md"), join(testDir, "test_readme.md"))
    
    
    
    
    
    
    
    