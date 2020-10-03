import re
import basic_http.exceptions.cookies

valid_attributes = ['expires', 'path', 'comment', 'domain', 'max-age', 'secure', 'version', 'httponly', 'samesize']


def parse_cookie(data: str, ignore_bad_cookie: bool = False):
    tokens = data.split(';')

    cookie = dict()

    try:
        name, value = tokens[0].split('=', 1)
    except ValueError:
        if not ignore_bad_cookie:
            raise basic_http.exceptions.cookies.BadCookie('Cookie syntax error.')
        else:
            return cookie

    name, value = name.strip(',; '), value.strip(',; ')
    cookie['name'] = name
    cookie['value'] = value

    for attribute in tokens[1:]:
        try:
            key, value = map(lambda v: v.strip(',; '), attribute.split('='))
        except ValueError:
            key, value = attribute.strip(',; '), True

        if not ignore_bad_cookie and key.lower() not in valid_attributes:
            raise basic_http.exceptions.cookies.BadCookie(f'Unknown attribute: \'{key}\'.')

        cookie[key] = value
    return cookie


def parse_set_cookie_header(header: str, ignore_bad_cookie: bool = False):
    tokens = [token.split('=', 1)[0].strip() for token in re.findall('[^ ]+[ ]*=[ ]*[^;,]+', header)]

    valid_tokens = [token for token in tokens if token.lower() not in valid_attributes]
    results = list()

    for token in valid_tokens[1:]:
        cookie_end_index = header.index(token)

        if not cookie_end_index:
            delta = len(token)
            cookie_end_index = header[delta:].index(token)
            cookie_end_index += delta

        results.append(parse_cookie(header[: cookie_end_index].strip(', '), ignore_bad_cookie))
        header = header[cookie_end_index:]
    else:
        results.append(parse_cookie(header.strip(', '), ignore_bad_cookie))

    return results
