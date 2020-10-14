# -*- coding: UTF-8 -*-
import os
import stat
import argparse
import requests
import paramiko


def get_flags():
  os.environ['COLUMNS'] = "132"
  cmd = argparse.ArgumentParser()
  cmd.add_argument('-s', '--server', type=str, required=True, metavar='<url>',
                   help='The Nexus server url')
  cmd.add_argument('-r', '--repository', type=str, required=True, metavar='<repo>',
                   help='The Nexus repository name, eg. maven-releases')
  cmd.add_argument('-u', '--username', type=str, required=True, metavar='<user>',
                   help='The Nexus login username')
  cmd.add_argument('-p', '--password', type=str, required=True, metavar='<pass>',
                   help='The Nexus login password')
  cmd.add_argument('-j', '--jar', type=str, nargs='+', required=True, metavar='<jar>',
                   help='Upload specific package jar(s), eg: com.alibaba:fastjson:jar:1.2.62')
  cmd.add_argument('-f', '--folder', type=str, required=True, metavar='<path>',
                   help='Upload package jars from local or remote path')
  cmd.add_argument('--ssh-server', type=str, metavar='<host:port>',
                   help='Remote ssh\'s host and port, eg: ssh.server.com:22')
  cmd.add_argument('--ssh-login', type=str, metavar='<user:pass>',
                   help='Remote ssh\'s username and password, eg: root:pass')
  flags = cmd.parse_args()
  # merge nexus api url
  from requests.compat import urljoin, urlparse
  flags.url = urljoin(flags.server, 'service/rest/v1/components?repository=%s' % flags.repository)
  flags.source = flags.folder
  # parse and validate ssh server info
  if flags.ssh_login:
    s = flags.ssh_login.split(":", 1)
    flags.ssh_user = s[0].strip()
    flags.ssh_pass = s[1].strip() if len(s) > 1 else ''
  if flags.ssh_server:
    p = urlparse('scp://' + flags.ssh_server)
    flags.ssh_host = p.hostname
    flags.ssh_port = p.port or 22
    flags.ssh_user = p.username or flags.ssh_user if hasattr(flags, 'ssh_user') else ''
    flags.ssh_pass = p.password or flags.ssh_pass if hasattr(flags, 'ssh_pass') else ''
    flags.source = '%s:%s/%s' % (flags.ssh_host, flags.ssh_port, flags.folder)
  if hasattr(flags, 'ssh_host') and not flags.ssh_user:
    raise cmd.error('the following arguments are invalid: --ssh-server/--ssh-login')
  # parse and validate package info
  flags.package = []
  for i in ' '.join(flags.jar).replace(',', ' ').split():
    split = i.split(':')
    if len(split) == 4:
      flags.package.append({
        'name': i,
        'groupId': split[0],
        'artifactId': split[1],
        'extension': split[2],
        'version': split[3],
      })
  if not len(flags.package):
    return cmd.error('the following arguments are invalid: -p/--package')
  return flags


def open_package(package, flags):
  files = [
    '%s.%s-%s.%s' % (package['groupId'], package['artifactId'], package['version'], package['extension']),
    '%s-%s.%s' % (package['artifactId'], package['version'], package['extension']),
    '%s.%s.%s' % (package['groupId'], package['artifactId'], package['extension']),
    '%s.%s' % (package['artifactId'], package['extension']),
  ]
  if hasattr(flags, 'ssh_host'):
    # noinspection PyTypeChecker
    transport = paramiko.Transport((flags.ssh_host, flags.ssh_port))
    transport.connect(username=flags.ssh_user, password=flags.ssh_pass)
    sftp = paramiko.SFTPClient.from_transport(transport)
    for f in files:
      # noinspection PyBroadException
      try:
        path = os.path.join(flags.folder, f)
        s = stat.S_IFMT(sftp.stat(path).st_mode or 0)
        if s != stat.S_IFREG:
          continue
      except Exception:
        continue
      return sftp.open(path, 'rb')
  else:
    for f in files:
      path = os.path.join(flags.folder, f)
      if not os.path.isfile(path):
        continue
      return open(path, 'rb')
  raise FileNotFoundError('path=%s, package=%s' % (flags.source, package['name']))


def upload_package(package, flags):
  print("Uploading package %s from %s..." % (package['name'], flags.source))
  auth = (flags.username, flags.password)
  headers = {
    'User-Agent': 'PowerShell',
    'accept': 'application/json',
  }
  files = {
    'maven2.asset1': open_package(package, flags),
  }
  data = {
    'maven2.groupId': package['groupId'],
    'maven2.artifactId': package['artifactId'],
    'maven2.version': package['version'],
    'maven2.asset1.extension': package['extension'],
    'maven2.generate-pom': 'true',
  }
  response = requests.post(flags.url, auth=auth, headers=headers, files=files, data=data)
  response.raise_for_status()
  print("Upload package %s success." % (package['name']))


def main():
  flags = get_flags()
  print("Start to upload packages %s to repository '%s' of Nexus server %s..." % (
    [i['name'] for i in flags.package], flags.repository, flags.server))
  for i in flags.package:
    upload_package(i, flags)
  print("Success to upload packages %s to repository '%s' of Nexus server %s" % (
    [i['name'] for i in flags.package], flags.repository, flags.server))


if __name__ == '__main__':
  main()
