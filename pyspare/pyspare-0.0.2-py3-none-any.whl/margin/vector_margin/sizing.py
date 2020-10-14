from veho.vector import length


def sizing(vec, head, tail):
    size = length(vec)
    if not size:
        return 0, 0
    elif (not head and not tail) or (head >= size):
        return size, 0
    else:
        return head, tail
