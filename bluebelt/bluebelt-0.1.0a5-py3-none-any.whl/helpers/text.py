import re

def get_nice_filters_name(filters):
    if filters is not None:
        text = str(filters)
        for i in ['{','[','}',']', '\'']:
            text = text.replace(i, '')
        return text
    else:
        return 'total'

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
