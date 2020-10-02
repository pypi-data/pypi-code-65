import urllib.request, urllib.parse, urllib.error
import sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))

print('Poppy Library v1.3.2')

if not os.path.isdir(dir_path + '/data'):
    os.mkdir(path=(dir_path + '/data/'))

try:
    with open(dir_path + '/data/ports.json') as ports:
        pass
except FileNotFoundError:
    print('Downloading port configuration!')

    f = urllib.request.urlopen('https://raw.githubusercontent.com/Allanzinh0/PopPyControl/master/PopPyControl/data/ports.json')
    data = f.read()
    with open(dir_path + '/data/ports.json', 'wb') as code:
        code.write(data)

try:
    with open(dir_path + '/data/motors.json') as motors:
        pass
except FileNotFoundError:
    print('Downloading motor configuration!')

    f = urllib.request.urlopen('https://raw.githubusercontent.com/Allanzinh0/PopPyControl/master/PopPyControl/data/motors.json')
    data = f.read()
    with open(dir_path + '/data/motors.json', 'wb') as code:
        code.write(data)
