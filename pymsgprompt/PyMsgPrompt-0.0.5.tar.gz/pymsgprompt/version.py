from pkg_resources import get_distribution
from email import message_from_string
import os

def _version():
    prog_name = "PyMsgPrompt"
    try:
        pkgInfo = get_distribution(prog_name).get_metadata('PKG-INFO')
    except:
        try:
            pkgInfo = get_distribution(prog_name).get_metadata('METADATA')
        except:
            pkgInfo = None
    if pkgInfo is not None:
        msg = message_from_string(pkgInfo)
        items = msg.items()
        for item, data in items:
            if item.upper() == 'VERSION':
                return (prog_name, data)
    else:
        import json
        try:
            data = json.load(open(
                os.path.abspath(os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'METADATA.json'
                ))
            ))
            version_info = data['version_info']
            prog_name = data['module_name']
            return (prog_name, version_info)
        except:
            pass
    return (prog_name, '<UNKNOWN VERSION>')
    
if __name__ == '__main__':
    os.sys.stdout.write('%s - %s\n'%_version())
