def linecost(x):
    return x
def cstcost(x):
    if x:
        return 1
    else:
        return 0
def expcost(x):
    if x:
        return 2**x
    else:
        return 0
def squarecost(x):
    if x:
        return x*x
    else:
        return 0

