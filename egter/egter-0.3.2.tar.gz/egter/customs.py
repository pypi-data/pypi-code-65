class List(list):
    """
    usage:

    from egter import customs
    List = customs.List
    lst = [0, 1, 4]
    print(lst.get(3, None))
    # None
    print(lst.get(2, None))
    # 4
    print(lst.get(3))
    # None

    equal to:
    d = {0: 0, 1: 1, 2: 4}
    print(d.get(4)
    # None
    """

    def get(self, i, ret=None):
        try:
            return self[i]
        except:
            return ret