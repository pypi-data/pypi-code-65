from collections import OrderedDict

class LRUCache(object):
    '''
    least recently used cache example
    '''

    def __init__(self, capacity=128):
        self.od = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.od:
            value = self.od.get(key)
            self.od.move_to_end(key) # 如果找到了那么将 该次访问的key移到队列最右端也就是最新的那一端
        else:
            value = -1  # 没有找到 返回 -1
        return value

    def put(self, key, value):
        if key in self.od:
            del self.od[key]
            self.od[key] = value
        else:
            self.od[key] = value
            if len(self.od) > self.capacity:
                self.od.popitem(last=False)  # 如果在新添加值进来后判断到 总元素个数超出了指定容量大小，那么将最左边的元素出队


if __name__ == '__main__':

    lru_cache = LRUCache(10)
    from string import ascii_lowercase
    for key, value in zip(range(10), ascii_lowercase):
        lru_cache.put(key, value)

    assert lru_cache.get(3) == 'd'
    assert lru_cache.get(3) is 'd'
    lru_cache.put(10,'k')

    for i in range(11):
        res = lru_cache.get(i)
        print(res, end=',')