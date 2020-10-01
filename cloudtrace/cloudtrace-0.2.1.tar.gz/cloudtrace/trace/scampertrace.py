import os
import random
import subprocess
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from cloudtrace.trace.fasttrace import fopen, new_filename, remote_notify


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--input')
    group.add_argument('-I', '--addr', nargs='*')
    parser.add_argument('-f', '--first-hop', type=int, default=1)
    parser.add_argument('-p', '--pps', default=8000, type=int, help='Packets per second.')
    parser.add_argument('-P', '--proto', default='icmp', choices=['icmp', 'udp'], help='Transport protocol.')
    parser.add_argument('-d', '--default-output', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-z', '--gzip', action='store_true')
    group.add_argument('-b', '--bzip2', action='store_true')
    parser.add_argument('-r', '--remote')
    parser.add_argument('-c', '--cycles', type=int, default=1)
    parser.add_argument('--tmp', default='.infile.tmp')
    args = parser.parse_args()

    cycle = 0
    while args.cycles == 0 or cycle < args.cycles:
        with open(args.tmp, 'w') as f:
            if args.input:
                with fopen(args.input, 'rt') as g:
                    for line in g:
                        addr, _, _ = line.rpartition('.')
                        addr = '{}.{}'.format(addr, random.randint(0, 255))
                        f.write('{}\n'.format(addr))
            else:
                f.writelines('{}\n'.format(addr) for addr in args.addr)

        filename = new_filename(args.default_output, args.proto, args.pps, 'warts', gzip=args.gzip, bzip2=args.bzip2)
        if args.gzip:
            write = '| gzip > {}'.format(filename)
        elif args.bzip2:
            write = '| bzip2 > {}'.format(filename)
        else:
            write = '-o {}'.format(filename)
        dirname, basename = os.path.split(args.default_output)
        pattern = os.path.join(dirname, '{}.warts*'.format(basename))
        if args.proto == 'icmp':
            proto = 'icmp-paris'
        elif args.proto == 'udp':
            proto = 'udp-paris'
        elif args.proto == 'tcp':
            proto = 'tcp'
        else:
            raise Exception('Unknown proto {}'.format(args.proto))
        cmd = 'sudo scamper -O warts -p {pps} -c "trace -P {proto} -f {first}" -f {infile} {write}'.format(pps=args.pps, proto=proto, first=args.first_hop, infile=args.tmp, write=write)
        print(cmd)
        start = time.time()
        subprocess.run(cmd, shell=True, check=False)
        end = time.time()
        secs = end - start
        mins = secs / 60
        hours = mins / 60
        print('Duration: {:,.2f} s {:,.2f} m {:,.2f} h'.format(secs, mins, hours))
        if args.remote:
            remote_notify(pattern, args.remote)
        try:
            cycle += 1
        except OverflowError:
            cycle = 1
