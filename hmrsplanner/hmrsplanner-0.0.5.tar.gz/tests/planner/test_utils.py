import itertools


class each_reset_wrapper:
    def __init__(self, gen):
        self.gen = gen


class iterFib:
    called = 0

    def fibo(self, x):
        print('init')
        self.called += 1
        i, j = 1, 1
        yield j
        while j <= x:
            _next = i + j
            yield _next
            print('x')
            self.called += 1
            i = j
            j = _next
        print('end')


def test_gen_conbination():
    fib1 = iterFib()
    fib2 = iterFib()

    def sum(seqa, seqb):
        return itertools.starmap(lambda x, y: x+y, itertools.product(seqa, seqb))
            
    # for i, j in itertools.product(fib1.fibo(3), fib2.fibo(3)):
    #     print(i)
    #     print(j)
    print('lets')
    for x in sum(fib1.fibo(3), fib2.fibo(3)):
        print(x)
    
    print('----')
    print(fib1.called)
    print(fib2.called)

