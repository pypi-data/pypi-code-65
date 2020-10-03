#!/bin/env python3

import sys
import subprocess

def main():
    args = sys.argv[1:]
    bin = f"kosciuszko-{args.pop(0)}"

    l = [bin]
    l.extend(args)

    try:
            subprocess.run(l)
    except FileNotFoundError:
            print("Command not found")

