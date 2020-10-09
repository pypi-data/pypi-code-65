def printTable(widths, data):

    row_format = "".join(["{:<" + str(w) + "}" for w in widths])

    for row in data:
        print(row_format.format(*row))
