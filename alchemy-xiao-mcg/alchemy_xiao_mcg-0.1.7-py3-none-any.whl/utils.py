# Utils functions and classes

def chunkIt(n, num, offset=0):
    avg = n / float(num)
    out = []
    last = 0.0

    while last < n:
        out.append([int(last + offset), int(last + offset + avg)])
        last += avg

    return out