import send2trash, time, os


start = time.time()
for i in range(200):
    open('123', 'w')
    os.remove('123')
    # send2trash.send2trash('123')
print(time.time() - start)