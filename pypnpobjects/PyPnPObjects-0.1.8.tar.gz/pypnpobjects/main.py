
from pypnpobjects import WMIStorePNPObjects
import argparse
import os
import re
from pkg_resources import get_distribution
from email import message_from_string

def get_version(metadata):
    for item, data in metadata:
        if item.upper() == 'VERSION':
            return data
    return 'UNKNOWN'

def main():
    prog_name = "PyPnPObjects"
    pkgInfo = get_distribution(prog_name).get_metadata('PKG-INFO')
    msg = message_from_string(pkgInfo)
    items = msg.items()
    version_info = get_version(items)
    # meta = Meta()
    # prog_name = meta.module_name
    # version_info = meta.version_info
    # development_status = meta.development_status

    # if development_status == 1:
    #     status = 'Planning'
    # elif development_status == 2:
    #     status = 'Pre-Alpha'
    # elif development_status == 3:
    #     status = 'Alpha'
    # elif development_status == 4:
    #     status = 'Beta'
    # elif development_status == 5:
    #     status = 'Production/Stable'
    # elif development_status == 6:
    #     status = 'Mature'
    # else:
    #     status = 'Inactive'
    
    parser = argparse.ArgumentParser(description='''
        This is a simple python module for win32 systems, to get pnp entity objects.
    ''', prog=prog_name)
    parser.add_argument('-select', dest='select', action='append', default=[], help='add a object to select')
    parser.add_argument('-where', dest='where', action='append', default=[], help='add a where condition')
    parser.add_argument('-ignore_case', dest='ignore_case', action='store_true', default=False, help='set case sensitivity')
    parser.add_argument('-operator', dest='operator', action='store', default='equal', type=str,
                help='set the comparision operator, must be either `equal` or `like`')
    parser.add_argument('-version', action='version', version='%(prog)s ' + (version_info))
    parser.add_argument('-meta', help='Show metadata information',action='store', default=None, dest='metadata', choices=msg.keys())
    parser.add_argument('-show-meta-props', help='Show metadata properties',action='store_true',
                        default=False, dest='meta_options')
    result = parser.parse_args()


    if result.metadata is not None:
        os.sys.stdout.write('---------------- {0} ----------------\n'.format(result.metadata))
        for key,value in items:
            if key.upper() == result.metadata.upper():
                os.sys.stdout.write('{0}\n'.format(value))
        exit(0)
    if result.meta_options:
        os.sys.stdout.write('The available meta properties are below\n')
        for id, meta_option in enumerate(msg.keys()):
            os.sys.stdout.write('{0} : {1}\n'.format(id + 1, meta_option))
        exit(0)

    if result.operator.lower().strip() not in ('like', 'equal'):
        os.sys.stderr.write('Fatal: Invalid value for option `-operator`, must be either `like` or `equal`\n')
        exit(-1)
    else:
        result.operator = result.operator.lower().strip()
    if len(result.select) == 0:
        result.select = ['*']
    where = dict()
    for cond in result.where:
        pat = r'^([a-zA-Z0-9]+)\s*\:\s*(.*)$'
        m = re.match(pat, cond.strip())
        if m is None:
            os.sys.stderr.write('Fatal: Invalid pattern for a where condition `{0}`\n'.format(cond))
            exit(-1)
        else:
            key, val = m.groups()
            where[key] = val
    with WMIStorePNPObjects() as wmipnp:
        proc_res = wmipnp.load()
        if proc_res[0] == 0:
            where['case_sensitive_comparision'] = not result.ignore_case
            where['comparision_operator'] = result.operator
            for dev in wmipnp.query(*result.select, **where):
                for prop, value in dev:
                    os.sys.stdout.write('{0}\t\t\t:{1}\n'.format(prop, value))
                os.sys.stdout.write('\n')
        else:
            os.sys.stderr.write('Error with code %d : %s\n'%(proc_res))

