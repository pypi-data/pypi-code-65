import re
from basic_http.data_structures.header import HttpHeader


def parse_response_line(response_line: str):
    tokens = re.findall('[^ ]+', response_line)
    http_protocol, status_code, status = tokens[: 2] + [' '.join(tokens[2:])]

    return {
        'http_protocol': http_protocol,
        'status_code': int(status_code),
        'status': status
    }


def parse_response_header(header: str):
    lines = header.split('\r\n')

    header = HttpHeader()
    for line in lines:
        name, value = line.split(':', 1)
        name, value = name.strip(' '), value.strip(' ')
        header.add_one(name, value)

    return header


def parse_http_response(http_response: bytes):
    parsed_response = {
        'response_line': None,
        'header': '',
        'body': b''
    }

    response_line, response_header = http_response.split(b'\r\n', 1)
    response_line = parse_response_line(str(response_line, 'utf-8'))
    parsed_response['response_line'] = response_line

    try:
        response_header, response_body = response_header.split(b'\r\n\r\n', 1)
    except ValueError:
        return parsed_response

    response_header = parse_response_header(str(response_header, 'utf-8'))
    parsed_response.update({
        'header': response_header,
        'body': response_body
    })

    return parsed_response
