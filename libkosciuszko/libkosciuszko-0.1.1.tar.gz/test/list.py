from libkosciuszko import Kosciuszko

kosciuszko = Kosciuszko('example@example.com', '/tmp/example.kos', batch=True, passphrase="example", debug=True)
ls = kosciuszko.list()
assert len(ls) == 1
assert ls[0] == "squashfs-root"

