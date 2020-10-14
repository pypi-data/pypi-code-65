#!/usr/bin/env python3
"""
A dynamic ansible inventory based on running linuxcontainers.

When invoked with --list, lxd-inventory.py will a json inventory based on
currently running containers.
"""

import argparse
import json
import shutil
import subprocess
import sys
import jq


class LxcInventory():
    """
    Use LxcInventory to create an ansible inventory that reflects
    currently running linux containers
    """
    def __init__(self):
        self.lxc_bin = shutil.which('lxc')
        assert (self.lxc_bin), "Could not find lxc executable in the PATH"
        self.inventory = {}

        self.list = self.lxc_list()

    def dump_inventory(self):
        """
        prints the json inentory to stdout
        """
        inv = {}
        hostvars = {}
        groups = []

        for item in self.list:
            hostvar = {}
            if item['vars']:
                hostvar = json.loads(item['vars'])

            hostvar['ansible_host'] = item['address']

            hostvars[item['name']] = hostvar

            if item['groups']:
                groups = item['groups'].split(',')
            groups.append('all')

            # pivot
            for group in groups:
                if group not in inv:
                    inv[group] = []
                inv[group].append(item['name'])

        inv['_meta'] = {'hostvars': hostvars}
        print(json.dumps(inv, sort_keys=True, indent=2))

    def lxc_list(self):
        """
        runs lxc ls to get the containers in json format
        """
        result = subprocess.run(
            [self.lxc_bin, 'ls', '--format=json'],
            stdout=subprocess.PIPE,
            check=True
        )
        j = json.loads(result.stdout.decode('UTF-8'))
        return jq.compile("""
            .[] |
            {
            name: .name,
            groups: .config["user.ansible.groups"],
            vars: .config["user.ansible.vars"],
            address: .state.network.eth0.addresses[0].address
            } |
            select(.address)
            """).input(j).all()


if __name__ == "__main__":
    # execute only if run as a script
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--list', action='store_true')
    ARGS = PARSER.parse_args()
    if ARGS.list:
        INVENTORY = LxcInventory()
        INVENTORY.dump_inventory()
        sys.exit(0)
    else:
        print("Use --list for actual inventory output")
        sys.exit(1)
