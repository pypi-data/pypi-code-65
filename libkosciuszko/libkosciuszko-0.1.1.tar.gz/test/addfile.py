from libkosciuszko import Kosciuszko

kosciuszko = Kosciuszko('example@example.com', '/tmp/example.kos', batch=True, passphrase="example", debug=True)
kosciuszko.addfile('example.txt', 'Hello, world!'.encode('utf-8'))
ls = kosciuszko.list()
assert len(ls) == 2
assert ls[1] == 'squashfs-root/example.txt'

data = kosciuszko.getfile('example.txt')
data = data.decode('utf-8')
assert data == "Hello, world!"
