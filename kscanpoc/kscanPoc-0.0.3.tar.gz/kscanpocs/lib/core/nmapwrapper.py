#!/usr/bin/env python
# coding:utf-8
# Author:  Hysia @ BAIDU.Inc QA.SSL--<zhouhaixiao@baidu.com>
# Purpose: 获取nmap的检测结果：存活ip、开放端口、服务名称、所用产品名称以及版本信息
# Created: 2012年12月31日

import os
import time
import tempfile
import uuid
from optparse import OptionParser
from pprint import pprint
from kscanpocs.lib.core.settings import IS_IDLE

try:
    from kscanpocs.lib.thirdparty import Parser
except:
    from nmapparse import Parser


def consume_time(secs):
    """格式化时间"""
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


class Nmap(object):
    def __init__(self, tid, port_list=None, temp_path=None, nmap_path='nmap'):
        '''
        http 80 8080 81
        smtp 25
        https 443
        mysql 3306
        mstsc 3389
        ftp 21
        ssh 22
        telnet 23
        pop 110
        '''
        self.timeout = 900
        self.tid = tid if tid else str(uuid.uuid4())
        self.port_list = port_list or '80,81,8000,8008,8080,8088,8888,1433,3306,3389,21,22,23,110,25,443'
        self.temp_path = temp_path if temp_path else tempfile.gettempdir()
        self.nmap_path = nmap_path
        self.live_hosts_xmlfile = os.path.join(self.temp_path, 'live_hosts_%s.xml' % self.tid)
        self.host_services_xmlfile = os.path.join(self.temp_path, 'host_services_%s.xml' % self.tid)

        # 加-n参数，不进行DNS查询，速度提升至少10倍
        # -sP：ping扫描； -oX：指定输出到哪个XML文件
        # -sS：TCP SYN扫描
        self.live_hosts_cmd = self.nmap_path + ' -sn -n -PE -PP -PS22,80,443,3389,8080,8888,10051 -oX %s/live_hosts_' + str(
            self.tid) + '.xml %s'
        self.live_hosts_syn_cmd = self.nmap_path + ' -sS -n -oX %s/live_hosts_' + str(self.tid) + '.xml %s'
        # self.host_services_cmd = self.nmap_path +' -sT -sV -Pn --open  -p'+ self.port_list + ' -oX %s/host_services_'+ str(self.tid) + '.xml --host-timeout %s %s'
        self.host_services_cmd = self.nmap_path + ' -sV -Pn --open  -p' + self.port_list + ' -oX %s/host_services_' + str(
            self.tid) + '.xml %s --max-retries 3 --max-rtt-timeout 1 --defeat-rst-ratelimit --host-timeout 1800'

    def get_live_hosts(self, ips):
        '''根据目标域名，IP，IP段获取存活主机列表'''
        self.up_hosts = []
        cmd = self.live_hosts_cmd % (self.temp_path, ips)
        # 或者用 subprocess.Popen(command, stdout = sys.stdout, shell=True),不过据传性能不及os.popen()
        # Deprecated since version 2.6: This function is obsolete. Use the subprocess module.
        os.popen(cmd)

        parser = Parser.Parser(self.live_hosts_xmlfile)
        session = parser.get_session()
        self.total_hosts = session.total_hosts
        self.up_hosts_num = session.up_hosts
        self.down_hosts_num = session.down_hosts
        for live_host in parser.all_hosts('up'):
            self.up_hosts.append(live_host.ip)
        '''
        if len(self.up_hosts) == 0:
            cmd = self.live_hosts_syn_cmd % (self.temp_path, ips)
            os.popen(cmd)
            parser = Parser.Parser(self.live_hosts_xmlfile)
            session = parser.get_session()
            self.total_hosts = session.total_hosts
            self.up_hosts_num = session.up_hosts
            self.down_hosts_num = session.down_hosts
            for live_host in parser.all_hosts('up'):
                self.up_hosts.append(live_host.ip)
        '''
        return self.up_hosts

    def get_host_services(self, ips):
        '''返回存活主机检测结果：主机开放端口，服务，以及软件版本信息
        例如检测域名 testphp.vulnweb.com 的结果：
        {u'176.28.50.165': [(u'21', u'ftp', u'ProFTPD', u'1.3.3e'),
                    (u'22', u'ssh', u'OpenSSH', u'5.3p1 Debian 3ubuntu7'),
                    (u'25', u'smtp', u'Postfix smtpd', ''),
                    (u'80', u'http', u'Apache httpd', ''),
                    (u'110', u'pop3', u'Courier pop3d', ''),
                    (u'443', u'http', u'Apache httpd', '')]}
        '''
        ret = {}

        cmd = self.host_services_cmd % (self.temp_path, ips)
        # 或者用 subprocess.Popen(command, stdout = sys.stdout, shell=True),不过据传性能不�)
        os.popen(cmd)

        parser = Parser.Parser(self.host_services_xmlfile)
        session = parser.get_session()
        for live_host in parser.all_hosts('up'):
            ip = live_host.ip
            services = []
            for port in live_host.get_ports('tcp', 'open'):
                s, script = live_host.get_service('tcp', port)
                if not s:
                    continue
                if s.name == 'http' and s.tunnel == 'ssl':
                    s.name = 'https'
                services.append((port, s.name, s.product, s.version, script))
            ret[ip] = services
        return ret

    def clean_file(self):
        """清理检测中生成的临时xml文件"""

        if os.path.exists(self.live_hosts_xmlfile):
            os.unlink(self.live_hosts_xmlfile)
        if os.path.exists(self.host_services_xmlfile):
            os.unlink(self.host_services_xmlfile)


def main(ips, tid='', port_list='', temp_path=None, nmap_path='nmap'):
    '''接口函数
    ips: 检测的IP
    tid: 用于标识任务id，便于查看结果
    temp_path: 中间输出结果的临时目录，如果未指定则为当前环境变量的临时目录
    nmap_path: 指定nmap可执行文件的路径，例如 "/usr/local/nmap/bin/nmap" ，默认为 "nmap"
    '''
    nmap_path = '/home/work/local/nmap/bin/nmap' if IS_IDLE \
                                                    and os.path.exists('/home/work/local/nmap/bin/nmap') \
        else nmap_path

    nmap = Nmap(tid, port_list, temp_path, nmap_path)

    live_hosts = nmap.get_live_hosts(ips)  # 首先获取存活主机
    live_ips = ' '.join(live_hosts)
    result = nmap.get_host_services(live_ips)

    try:
        nmap.clean_file()  # 清理生成的临时文件
    except Exception as e:
        print('clean nmap temp xml file failed: %s' % e)

    return result


if __name__ == '__main__':

    usage = "python get_nmap_result.py -t 192.168.10.1-254"
    parser = OptionParser(usage)
    parser.add_option("-t", "--target", dest="target", default="",
                      help="domain,ip or ip range to be scaned, eg: 192.168.10.2 192.168.10.1-254 192.168.10.*")
    parser.add_option("-p", "--port", dest="port", default="",
                      help="port range to be scaned, eg: 21,22,80,100-300,8080")
    (options, args) = parser.parse_args()

    if not options.target:
        print
        'please show me the target host!'
        parser.print_help()
    else:
        target = options.target
        start_time = time.time()
        print
        "[*] Starting at: %s" % time.strftime("%x %X")
        print
        '[*] Scanning target: %s ...' % target
        result = main(target, port_list=options.port)
        print
        '[*] Scan result:'
        pprint(result)
        print
        '[*] Done.'
        end_time = time.time()
        print
        "[*] Shutting down at: %s, consumed time: %s" % (time.strftime("%x %X"), consume_time(end_time - start_time))
