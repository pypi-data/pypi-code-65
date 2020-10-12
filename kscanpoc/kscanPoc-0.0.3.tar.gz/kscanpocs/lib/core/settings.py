#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose:
# Created: 2012年12月31日

import os
import platform
import sys
import subprocess

VERSION = "1.0-dev"
VERSION_STRING = "LVScanner(hostscan)/%s" %VERSION
DESCRIPTION = "SSL & QA"
SITE = "http://scan.baidu.com"

# System variables
IS_WIN = subprocess.mswindows

IS_IDLE = 'vm.baidu.com' in platform.node()

# The name of the operating system dependent module imported. The following names have currently been registered: 'posix', 'nt', 'mac', 'os2', 'ce', 'java', 'riscos'
PLATFORM = os.name
PYVERSION = sys.version.split()[0]

# Encoding used for Unicode data
UNICODE_ENCODING = "utf8"

# Format used for representing invalid unicode characters
INVALID_UNICODE_CHAR_FORMAT = r"\?%02x"

# Strftime format for results file used in multiple target mode
RESULTS_FILE_FORMAT = "results-%m%d%Y_%I%M%p.csv"
