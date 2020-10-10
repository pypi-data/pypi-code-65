import sys
import time


i   = 0
ids = 1000

myresults = []

while i <= 100:

    time.sleep(0.5)
    sys.stderr.write("\rDownloading metadata (%6.2f%%)" % (i*100/100))
    sys.stderr.flush()
    myresults.append('deep breath')
    # out += tmp_out
    i   += 10

sys.stderr.write('\n')
sys.stderr.flush()


for mr in myresults:
    sys.stdout.write(mr + "\n")
    sys.stdout.flush()

