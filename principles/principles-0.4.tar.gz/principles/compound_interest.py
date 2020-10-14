def compound_interest(capital, interest_rate, iterations):
    """Computes compound interest
    >>> print(compound_interest(100, 9.1, 3))
    [109.1, 228.1281, 357.9877571]
    """
    results = []
    cummulative_total = 0

    for i in range(0, iterations):
        cummulative_total += capital
        cummulative_total *= (interest_rate / 100) + 1
        results.append(cummulative_total)

    return results

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    #print(compound_interest(25, 100, 3))
