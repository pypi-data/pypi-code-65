from libkosciuszko import Kosciuszko

kosciuszko = Kosciuszko('example@example.com', '/tmp/example.kos', batch=True, passphrase="example", debug=True)
kosciuszko.new()
