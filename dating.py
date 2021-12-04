from txtools import writeTxt1, readTxtStr

# give each price change an index (in order). For each stock, graph the price at that index, using NaN to fill in the blanks.

i = int(readTxtStr("data/dated.txt"))

def date():
    global i
    i += 1
    writeTxt1("data/dated.txt", i)
    return i