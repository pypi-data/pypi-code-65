import random

class Stenography:
    """
    import egter_test.crypt as crypt
    import egter_test.crypt.defaults as defaults

    s = crypt.Stenography(defaults.stenography_list)
    enc = s.encode(b'some bytes')
    dec = s.decode(enc)
    print(enc, dec)
    # Viverra facilisisu eue nisla elita nisio luctuso litorae, nisla; viverra b'some bytes'
    """

    def __init__(self, stenography_list, punctuation=',:;!?.', punctuation_end='!?.'):
        self.stenography_list = stenography_list
        self.punctuation = punctuation
        self.punctuation_end = punctuation_end

    def encode(self, bt):
        out = ''
        pl = 0
        up = True
        for i in range(len(bt)):
            try:
                f = str(bt[i + pl])
                try:
                    s = str(bt[i + 1 + pl])
                    n = f + ':' + s
                except:
                    s = False
                    n = False
                if s and random.choice([True, True, False]):
                    if n in self.stenography_list:
                        pl += 1
                        if up:
                            out += self.stenography_list[n].title()
                            up = False
                        else:
                            out += self.stenography_list[n]
                    else:
                        if up:
                            out += self.stenography_list[f].title()
                            up = False
                        else:
                            out += self.stenography_list[f]
                else:
                    if up:
                        out += self.stenography_list[f].title()
                        up = False
                    else:
                        out += self.stenography_list[f]
                if random.choice([True, False, False, False, False]):
                    punc = random.choice(self.punctuation)
                    out += punc
                    if punc in self.punctuation_end:
                        up = True
                out += ' '
            except:
                pass
        out = out.strip()
        return out

    def decode(self, out):
        out = out.lower()
        for i in self.punctuation:
            out = out.replace(i, '')
        spl = out.split()
        bt = []
        for word in spl:
            for i in self.stenography_list:
                if self.stenography_list[i] == word:
                    s = i.split(':')
                    for k in s:
                        bt.append(int(k))
        bt = bytes(bt)
        return bt