import hashlib
import base64
import ipaddress
from fire import Fire


def htpasswd(user, password, filepath=None):
    # from https://httpd.apache.org/docs/2.4/misc/password_encryptions.html
    hashed_password = base64.b64encode(
        hashlib.sha1(password.encode()).digest()
    ).decode()
    token = f"{user}:{{SHA}}{hashed_password}"
    if filepath is not None:
        with open(filepath, "w") as file_pointer:
            file_pointer.write(token + "\n")

    return token


def ip_in_cidr(cidr, following=None):

    condition = following is None
    for i, ip in enumerate(ipaddress.ip_network(cidr)):
        if i == 0:
            continue

        if condition:
            return str(ip)

        if following == str(ip):
            condition = True

    return None


if __name__ == "__main__":
    Fire()
