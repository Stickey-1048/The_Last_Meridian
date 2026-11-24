"""Original typed VMAD reader carried from Sam source review tooling."""
import struct
def vmad(data):
    pos = 0
    def take(n):
        nonlocal pos
        assert pos+n <= len(data)
        value = data[pos:pos+n]; pos += n
        return value
    def number(fmt): return struct.unpack(fmt, take(struct.calcsize(fmt)))[0]
    def string(): return take(number('<H'))
    version, objformat, count = struct.unpack('<HHH', take(6))
    assert objformat == 2
    def value(kind):
        start = pos
        if kind == 1: take(8)
        elif kind == 2: string()
        elif kind in (3,4): take(4)
        elif kind == 5: take(1)
        elif kind in (11,12,13,14,15):
            for _ in range(number('<I')): value(kind-10)
        else: raise AssertionError(f'Unsupported VMAD type {kind}')
        return data[start:pos]
    scripts = []
    for _ in range(count):
        name, status, n = string(), number('<B'), number('<H')
        props = []
        for _ in range(n):
            pname, kind, state = string(), number('<B'), number('<B')
            props.append((pname, kind, state, value(kind)))
        scripts.append((name, status, props))
    return (version, objformat), scripts, data[pos:]

