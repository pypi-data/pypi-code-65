#!/usr/bin/env python3
import time
import csv
from scapy.all import ARP, Ether, srp, get_if_addr, get_if_hwaddr, conf


def arp_scan(ip):
    """
    Performs a network scan by sending ARP requests to an IP address or a range of IP addresses.
    Args:
        ip (str): An IP address or IP address range to scan. For example:
                    - 192.168.1.1 to scan a single IP address
                    - 192.168.1.1/24 to scan a range of IP addresses.
    Returns:
        A list of dictionaries mapping IP addresses to MAC addresses. For example:
        [
            {'IP': '192.168.2.1', 'MAC': 'c4:93:d9:8b:3e:5a'}
        ]
    """
    conf.verb = 0
    
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)

    ans, unans = srp(request, timeout=2, retry=1)
    result = []

    for sent, received in ans:
        result.append({'IP': received.psrc, 'MAC': received.hwsrc})
    return result


def scan(scan_log_filename: str, output_log_filename: str):
    current_time = time.time()
    host_mac = get_if_hwaddr(conf.iface)
    host_ip = get_if_addr(conf.iface)
    results = arp_scan("10.0.0.1/24")
    
    # CSV A
    # scan_timestamp,mac_of_scanner,mac_of_target,ip_of_target
    with open(output_log_filename, 'a+') as f:
        writer = csv.writer(f)
        for result in results:
            writer.writerow([current_time,host_mac,result['MAC'],result['IP']])
    # CSV B
    # scan_timestamp,mac_of_scanner,ip_of_scanner
    with open(scan_log_filename, 'a+') as f:
        writer = csv.writer(f)
        writer.writerow([current_time, host_mac, host_ip])


if __name__ == "__main__":
    scan('scan-log.csv', 'output-log.csv')
