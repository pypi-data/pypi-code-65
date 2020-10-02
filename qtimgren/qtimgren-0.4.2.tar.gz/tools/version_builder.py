#  Copyright (c) 2020  SBA - MIT License

"""
This is a utility file aimed at building a VERSIONINFO resource for
pyinstaller on Windows.
It is intended to be used from the top-level project folder (the one
containing setup.py
"""

import re

rx = re.compile(r'(\d+)\.(\d+).(\d+)(.*)')
dist = re.compile(r'.dev(\d+)+')
dirty = re.compile(r'.*d\d{6}$')

mask = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({v1}, {v2}, {v3}, {v4}),
    prodvers=({v1}, {v2}, {v3}, {v4}),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x{flags:x},
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'000004b0',
        [StringStruct(u'Comments', u'GUI frontend over pyimgren to rename digital camera images.'),
        StringStruct(u'CompanyName', u'SBA'),
        StringStruct(u'FileDescription', u'QtImgren'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2020  SBA - MIT License'),
        StringStruct(u'OriginalFileName', u'QtImgren'),
        StringStruct(u'ProductName', u'QtImgren'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [0, 1200])])
  ]
)
'''


def build(v1, v2, v3, v4, flags, version):
    return mask.format(v1=v1, v2=v2, v3=v3, v4=v4, flags=flags,
                       version=version)


def parse_version(v):
    flags = 0
    m = rx.match(v)
    v1, v2, v3, extra = m.groups()
    v4 = 0
    extra = extra.strip()
    if extra != '':
        flags |= 2
        if extra.startswith('.dev'):
            v3 = str(int(v3) - 1)
            m = dist.match(extra)
            if m:
                v4 = str(int(m.group(1)) + 1)
        m = dirty.match(extra)
        if m:
            flags |= 4
    return v1, v2, v3, v4, flags


def run(version):
    v1, v2, v3, v4, flags = parse_version(version)
    with open('file_version_info.txt', 'w') as fd:
        fd.write(build(v1, v2, v3, v4, flags, version))
    print('Built file_version_info.txt for {} ({}.{}.{}.{})'.format(
        version, v1, v2, v3, v4))


if __name__ == '__main__':
    from qtimgren.version import version as app_version

    run(app_version)
