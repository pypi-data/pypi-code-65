#!/usr/bin/env python
import sys
import importlib


if __name__ == '__main__':
    if not  sys.version_info[0] == 3:
        print('Python3 required')
        exit(-1)
    __mod = importlib.import_module('ciphit.ciphitapp')
    __attr = {i:j for i,j in __mod.__dict__.items() if not i.startswith('_')}
    locals().update(__attr)
    main()
