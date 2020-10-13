# Author:
#  Romain Bentz (pixis - @hackanddo)
# Website:
#  https://beta.hackndo.com

"""
RENAME THIS FILE TO tests_config.py
"""

# Include Kerberos authentication tests
# This test requires to have a valid TGT for a local admin set in KRB5CCNAME
# See https://github.com/Hackndo/lsassy/wiki/Lsassy-Advanced-Usage#kerberos
kerberos = True

# Domain controller FQDN or IP, only needed if kerberos set to True
domain_controller = "10.10.10.1"

# If kerberos is set to True, FQDN of a valid target. IP address otherwise.
target = "dc01.hackn.lab"

# If kerberos is set to True, FQDN of target where LSASS is protected. IP address otherwise. (empty to skip tests)
protected_target = ""

# Domain Name
domain = "hackn.lab"

# User with admin rights on target and protected_target
da_login = "Administrator"
da_password = "You're da boss now :)"

# User without admin rights on target (empty to skip tests)
usr_login = "arodgers"
usr_password = "dancing_queen101"

# Local tools for dumping methods (empty to skip tests)
procdump_path = "/opt/procdump.exe"
dumpert_path = "/opt/dumpert.exe"