from decimal import Decimal


def Binominal(n: int, k: int) -> int:
    if k > n:
        return 0
    result = 1
    if k > n - k:
        k = n - k
    i = 1
    while i <= k:
        result *= n
        result //= i
        n -= 1
        i += 1
    return result


def pvalue(a: int, b: int,
           c: int, d: int) -> Decimal:
    return (Decimal(Binominal(a + b, a)
                    * Binominal(c + d, c))
            / Decimal(Binominal(a + b + c + d, a + c)))


def FisherLeftSide(a: int, b: int,
                   c: int, d: int,
                   baseP: Decimal) -> float:
    p = 0.0
    curP = float(baseP)
    while(a > 0 and d > 0):
        curP *= a * d
        a -= 1
        b += 1
        c += 1
        d -= 1
        curP /= b * c
        if curP <= baseP:
            p += curP
    return p


def FisherRightSide(a: int, b: int,
                    c: int, d: int,
                    baseP: Decimal) -> float:
    p = float(0)
    curP = float(baseP)
    while(b > 0 and c > 0):
        curP *= b * c
        a += 1
        b -= 1
        c -= 1
        d += 1
        curP /= a * d
        if curP <= baseP:
            p += curP
    return p


def FisherExact(a: int, b: int,
                c: int, d: int) -> Decimal:
    """Calculate two-tailed Fisher's exact test for 2x2 continguency table

    Args:
        a: column 1 row 1
        b: column 2 row 1
        c: column 1 row 2
        c: column 2 row 2

    Returns:
        Result of two-tailed Fisher's exact test stored in Decimal class
    """
    if a == b == c == d:
        return Decimal(1)
    p = t = pvalue(a, b, c, d)
    leftTail = Decimal(FisherLeftSide(a, b, c, d, t))
    p += leftTail
    rightTail = Decimal(FisherRightSide(a, b, c, d, t))
    p += rightTail
    return p
