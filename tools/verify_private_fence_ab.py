"""Read-only raw preservation/coarse bounds audit; no native visual proof."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib
from check_plugin_layout import records, subrecords


def load_records(path):
    buf = path.read_bytes()
    result = {}
    for kind, off, size, form, flags in records(buf, 0, len(buf)):
        data = buf[off:off + size]
        if flags & 0x40000:
            data = zlib.decompress(data[4:])
        parts = list(subrecords(data))
        name = next((v.rstrip(b'\0').decode() for k, v in parts if k == 'EDID'), '')
        key = kind, form
        assert key not in result, key
        result[key] = (buf[off-24:off+size], parts, name)
    return buf, result


def gap(x, y, box):
    return math.hypot(max(box['minX']-x, 0, x-box['maxX']),
                      max(box['minY']-y, 0, y-box['maxY']))


def audit(control, specimen):
    old_bytes, old = load_records(control / 'TLMWorldSlice.esp')
    new_bytes, new = load_records(specimen / 'TLMWorldSlice.esp')
    assert old.keys() == new.keys(), 'record allocation changed'
    data = json.loads((specimen / 'private-fence-comparison.json').read_text())
    expected = {row['id'] for row in data['swaps']}
    rows = {row['id']: row for row in data['swaps']}
    assert len(expected) == 16
    changed = []
    for key, (raw, parts, name) in old.items():
        if raw == new[key][0]:
            continue
        assert key[0] == 'REFR' and name in expected, (key, name)
        assert new[key][2] == name
        assert [p for p in parts if p[0] != 'NAME'] == [p for p in new[key][1] if p[0] != 'NAME'], name
        assert [v for k, v in parts if k == 'NAME'] == [struct.pack('<I', 0x125C67)]
        assert [v for k, v in new[key][1] if k == 'NAME'] == [struct.pack('<I', 0x3622D)]
        assert raw[:24] == new[key][0][:24], 'reference header/flags changed'
        at = struct.unpack('<6f', next(v for k, v in new[key][1] if k == 'DATA'))
        row = rows[name]
        assert all(abs(a-b) < .001 for a, b in zip(at, (row['x'], row['y'], row['z'], 0, 0, row['yaw']))), name
        changed.append(name)
    assert set(changed) == expected
    assert len(old_bytes) == len(new_bytes)
    # The only whole-file byte differences must lie in those NAME subrecords.
    assert sum(a != b for a, b in zip(old_bytes, new_bytes)) == 48
    yards = [r for r in old.values() if r[2].startswith('TLM_WS_Yard')]
    boundaries = [r for r in old.values() if r[2].startswith('TLM_WS_Boundary')]
    assert len(yards) == 34 and len(boundaries) == 120
    for filename in ('world-story.json', 'world-expansion.json'):
        assert (control / filename).read_bytes() == (specimen / filename).read_bytes(), filename
    a = json.loads((control / 'world-slice.json').read_text())
    b = json.loads((specimen / 'world-slice.json').read_text())
    assert a.keys() == b.keys()
    old_places = {p['id']: p for p in a.pop('placements')}
    new_places = {p['id']: p for p in b.pop('placements')}
    assert a == b and old_places.keys() == new_places.keys()
    story_count = sum(kind in ('REFR', 'ACHR') and item[2].startswith('TLM_WS_ST_')
                      for (kind, form), item in old.items())
    assert len(old_places) == 285 and story_count == 29
    for name, placement in old_places.items():
        after = new_places[name].copy()
        if name in expected:
            after['base'] = placement['base']
        assert placement == after, name
    bounds = json.loads((specimen / 'world-clearance.json').read_text())
    old_bounds = json.loads((control / 'world-clearance.json').read_text())
    assert bounds['protectedPoints'] == old_bounds['protectedPoints']
    obstacles = bounds['obstacles']
    selected = {p['id']: p for p in obstacles if 'TLM_WS_' + p['id'] in expected}
    assert len(selected) == 16
    # Verify every new AABB from the audited local origin and builder yaw convention.
    for row in data['swaps']:
        corners = [(row['x'] + x*math.cos(row['yaw']) + y*math.sin(row['yaw']),
                    row['y'] + y*math.cos(row['yaw']) - x*math.sin(row['yaw']))
                   for x in (-64, 64) for y in (-15, 5)]
        box = selected[row['id'].removeprefix('TLM_WS_')]
        for field, value in (('minX', min(x for x, y in corners)), ('maxX', max(x for x, y in corners)),
                             ('minY', min(y for x, y in corners)), ('maxY', max(y for x, y in corners))):
            assert abs(box[field] - value) < .001, (row['id'], field)
    expansion = json.loads((specimen / 'world-expansion.json').read_text())
    routes = [a['mainRoute'], a['bypassRoute']] + [r['points'] for r in expansion['routes']]
    minimum = math.inf
    samples = 0
    for route in routes:
        for p, q in zip(route, route[1:]):
            for tick in range(101):
                t = tick/100
                x, y = p['x']*(1-t)+q['x']*t, p['y']*(1-t)+q['y']*t
                minimum = min(minimum, *(gap(x, y, box) for box in obstacles))
                samples += 1
    assert minimum >= 96
    standing = min(gap(p['x'], p['y'], box) for p in bounds['protectedPoints'] for box in selected.values())
    assert standing >= 128
    # North specimen is deeper toward the supply shelter, with no rear route promised.
    north = [p for name, p in selected.items() if name.startswith('BoundaryNorth')]
    supply = [p for p in obstacles if p['id'].startswith('EX_Supply')]
    margin = min(fence['minY']-building['maxY'] for fence in north for building in supply
                 if max(fence['minX'], building['minX']) < min(fence['maxX'], building['maxX']))
    assert margin > 0
    return dict(controlSha256=hashlib.sha256(old_bytes).hexdigest().upper(),
                specimenSha256=hashlib.sha256(new_bytes).hexdigest().upper(),
                majorRecords=len(old), changedRecords=16, unchangedMajorRecords=len(old)-16,
                onlyChangedSubrecord='NAME', totalChangedFileBytes=48,
                unchangedYardPanels=len(yards), unchangedBoundaryControls=len(boundaries)-len(changed),
                unchangedShellReferences=len(old_places)-len(changed), unchangedStoryReferences=story_count,
                unchangedStoryAndExpansionJson=True, routeSamples=samples,
                minimumRouteAabbDistance=minimum, requiredRouteRadius=96,
                protectedStoryPoints=len(bounds['protectedPoints']), minimumChangedFenceStandingDistance=standing,
                requiredStandingRadius=128, northSupplyGroundObstacleMargin=margin,
                gateway='All original gateway/yard records byte-identical;240 clear/214 underside unchanged',
                nativeAcceptance='No color/material/sockets/Havok/edge containment/walking acceptance', swaps=data['swaps'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('control', type=Path)
    parser.add_argument('specimen', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.control, args.specimen), indent=2))
