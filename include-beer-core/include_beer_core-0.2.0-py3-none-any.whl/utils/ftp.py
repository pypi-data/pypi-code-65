#!/usr/bin/env python3
from ftplib import FTP, FTP_TLS

def connect_tls(host, user, password):
    ftps = FTP_TLS(host)
    ftps.login(user, password)
    return ftps

