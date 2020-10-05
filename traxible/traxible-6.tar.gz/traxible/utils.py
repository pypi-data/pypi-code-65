import ipaddress
from fire import Fire


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
