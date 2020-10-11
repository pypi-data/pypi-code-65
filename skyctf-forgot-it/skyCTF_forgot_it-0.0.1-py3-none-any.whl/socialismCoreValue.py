# coding:utf8
import random


def encode(s):
    h = "富强民主文明和谐自由平等公正法治爱国敬业诚信友善"
    res = []
    if type(s) == str:
        s = s.encode()
    assert type(s) == bytes
    for x in s:
        for i in hex(x)[2:]:
            if i <= '9':
                res.append(int(i))
            else:
                if random.random() < 0.5:
                    res.append(10)
                    res.append(int(i, 16) - 10)
                else:
                    res.append(11)
                    res.append(int(i, 16) - 6)
    res = [h[i * 2:i * 2 + 2] for i in res]
    return ''.join(res)


def decode(s):
    assert type(s) == str
    # s = '''富强民主文明和谐自由平等公正法治爱国敬业诚信友善'''
    # s = [s[i:i+2] for i in range(0,len(s),2)]
    # s2i = dict(zip(s, range(0, 12)))
    s2i = {'富强': 0, '民主': 1, '文明': 2, '和谐': 3, '自由': 4, '平等': 5, '公正': 6, '法治': 7, '爱国': 8, '敬业': 9, '诚信': 10, '友善': 11}
    res = []
    i = 0
    while i < len(s):
        n = s2i[s[i:i + 2]]
        if n < 10:
            n = str(n)
            i += 2
        elif n == 10:
            n = hex(10 + s2i[s[i + 2:i + 4]])[2]
            i += 4
        elif n == 11:
            n = hex(s2i[s[i + 2:i + 4]] + 6)[2]
            i += 4
        res.append(n)
    res = [int(res[i * 2] + res[i * 2 + 1], 16) for i in range(len(res) // 2)]
    res = bytes(res).decode()
    return res


if __name__ == '__main__':
    pass
