

coins = [1, 5, 10, 25, 50, 100, 200, 500, 1000, 2000, 5000, 10000]

ccount = [i for i in range(10000 + 1)]
cselection = [None for i in range(10000 + 1)]

for c in coins:
    ccount[c] = 1
    cselection[c] = (c)


for i in range(10000):
    if ccount[i] <= 1:
        continue
    else:
        t = ccount[i]
        for j in range(0, i):
            s = ccount[j] + ccount[i-j]
            if s < t:
                t = s
                cselection[i] = (cselection[j], cselection[i-j])
        ccount[i] = t
        print(f'{i}:{t}')


max = 0
maxi = 0
for i in range(10000):
    if(ccount[i] > max):
        max = ccount[i]
        maxi = i

print(f'>{maxi}:{max}')
print(f'>{maxi}:{cselection[maxi]}')
