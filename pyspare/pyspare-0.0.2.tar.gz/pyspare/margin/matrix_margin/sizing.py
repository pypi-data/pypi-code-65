from veho.matrix import size


def sizing(mx, tp, bt, lf, rt, ht=None, wd=None):
    if not ht or not wd: (ht, wd) = size(mx)
    if not ht or not wd: tp, bt = 0, 0
    if (not tp and not bt) or (tp + bt >= ht): tp, bt = ht, 0
    if (not lf and not rt) or (lf + rt >= wd): lf, rt = wd, 0
    return tp, bt, lf, rt, ht, wd
