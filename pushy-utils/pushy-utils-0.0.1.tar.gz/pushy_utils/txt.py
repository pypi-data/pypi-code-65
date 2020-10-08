import base64


# base64 utils

def base64_encode(s):
    return base64.b64encode(s.encode()).decode('utf-8')


def base64_decode(s):
    return base64.b64decode(s).decode('utf-8')
