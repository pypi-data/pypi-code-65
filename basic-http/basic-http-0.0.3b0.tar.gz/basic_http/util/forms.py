import binascii
import os
from typing import Iterable


def encode_multipart_formdata(form: dict, charset: str = 'utf-8') -> tuple:
    # get a boundary
    boundary = '--------------------------' + binascii.hexlify(os.urandom(16)).decode('ascii')

    # form body
    body = bytes()
    # iterate over all fields in form
    for field in form.items():
        field_name = field[0]
        # set field header
        body += bytes(f'--{ boundary }\r\nContent-Disposition: form-data; name="{ field_name }"', charset)
        # if field value is list / tuple, we have a file
        if isinstance(field[1], Iterable):
            file_name = os.path.basename(field[1][0])
            file_content = field[1][1]
            
            # set file name and content type
            body += bytes(f'; filename="{ file_name }"\r\nContent-Type: application/octet-stream\r\n\r\n', charset)

            try:
                body += bytes(file_content)
            except TypeError:
                body += bytes(file_content, 'utf-8')

            # if file content is a byte stream, ok, just set it into body
            # if isinstance(file_content, bytes):
            #     body += file_content
            # otherwise, if file descriptor was provided, read file content
            # elif hasattr(file_content, 'read'):
            #     body += file_content.read()  # and set file content to body
        else:  # if regular chars string provided as argument
            # just encode it and set into form body
            body += bytes('\r\n\r\n', charset)
            body += bytes(field[1], charset)
        body += bytes('\r\n', charset)
    body += bytes(f'--{boundary}--\r\n', charset)

    # body = (
    #         ''.join('--%s\r\n'
    #                 'Content-Disposition: form-data; name=\'%s\'\r\n'
    #                 '\r\n'
    #                 '%s\r\n' % (boundary, field, value)
    #                 for field, value in form.items()) +
    #         '--%s--\r\n' % boundary
    # )

    content_type = "multipart/form-data; boundary=%s" % boundary
    return body, content_type
