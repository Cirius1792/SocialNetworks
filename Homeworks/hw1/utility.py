

def bar_diag(data):
    m, M = min(data), max(data)
    lb = m - m/10
    ub = M + M/10
    x = []