import re

def get_nice_polynomial_name(shape):
    if shape==0:
        return 'linear'
    if shape==1:
        return str(shape)+'st degree polynomial'
    elif shape==2:
        return str(shape)+'nd degree polynomial'
    elif shape==3:
        return str(shape)+'rd degree polynomial'
    else:
        return str(shape)+'th degree polynomial'

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
