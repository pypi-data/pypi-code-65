def suma_rek(lst):
    if len(lst) == 1:
        return lst[0]
    else:
        elem = lst.pop()
        return elem + suma_rek(lst)