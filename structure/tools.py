def deconstruct(element, le):
    b = 0
    o = 0
    lo = []
    for x in le:
        n = 0
        for j in range(x):
            n += bool(element[o]&(1<<b))<<j
            b += 1
            if b==8:
                o += 1
                b = 0
        lo.append(n)
    return lo

def construct(li, le):
    b = 0
    element = bytearray()
    for i, x in enumerate(le):
        n = li[i]
        for j in range(x):
            if b==0:
                element += bytes(1)
            element[-1] |= bool(n&(1<<j))<<b
            b += 1
            if b==8:
                b = 0
    return element

def createsource(match):
    source = []
    for i in range(256):
        nb = i
        for j in range(8):
            if nb&1:
                nb >>= 1
                nb ^= match
            else:
                nb >>= 1
        source.append(nb)
    return source

def calcsum(source, buffer):
    sum = 0xFFFFFFFF;
    for b in buffer:
        sum = source[(b^sum)&0xFF]^(sum>>8)
    return sum^0xFFFFFFFF
