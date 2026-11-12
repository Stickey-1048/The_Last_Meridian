#!/usr/bin/env python3
"""Checks the bytes of the built plugin's quest records, without the library that wrote them.

Why this exists: the library that writes the plugin (Mutagen) also reads back,
without complaint, a quest whose stages lack the subrecord that starts a stage
item (QSDT). The game does not treat such a stage the same way: on 2026-11-12
the stages could be set in the game but no OnStageSet event reached the quest
scripts. A check that reads the file through the same library cannot see that,
so this one reads the raw records.

What it asserts for every quest (QUST) record:
  - the marker between the two condition lists (NEXT) is present;
  - every stage (INDX) is followed at once by an item's flags (QSDT), and has
    exactly one item;
  - nothing that belongs to an item (CTDA, NAM2, CNAM, NAM0) appears in a stage
    before a QSDT;
  - every objective (QOBJ) is followed at once by its flags (FNAM).

The layout is the one in xEdit's record definitions for Fallout 4
(wbDefinitionsFO4.pas, record QUST). It is a check of the file's shape. It
does not prove what the game does with it.

Usage:  check_plugin_layout.py <plugin.esp>     exit 0 if the layout is as expected
        check_plugin_layout.py --self-test <plugin.esp>
            also damages copies of the file in memory and requires each kind
            of damage to be caught
"""
import struct
import sys
import zlib

ITEM_PARTS = {"CTDA", "CIS1", "CIS2", "NAM2", "CNAM", "NAM0"}


def records(buf, start, end):
    """Yields (type, data_offset, data_size, formid, flags) for every record, descending into groups."""
    i = start
    while i < end:
        kind = buf[i:i + 4].decode("latin1")
        if kind == "GRUP":
            size = struct.unpack_from("<I", buf, i + 4)[0]
            if size < 24:
                raise ValueError(f"group at {i} has size {size}")
            yield from records(buf, i + 24, i + size)
            i += size
        else:
            size, flags, formid = struct.unpack_from("<III", buf, i + 4)
            yield kind, i + 24, size, formid, flags
            i += 24 + size


def subrecords(data):
    """Yields (type, bytes). Handles the XXXX size-override subrecord."""
    i = 0
    override = None
    while i < len(data):
        kind = data[i:i + 4].decode("latin1")
        size = struct.unpack_from("<H", data, i + 4)[0]
        if kind == "XXXX":
            override = struct.unpack_from("<I", data, i + 6)[0]
            i += 6 + size
            continue
        if override is not None:
            size, override = override, None
        yield kind, data[i + 6:i + 6 + size]
        i += 6 + size


def quest_records(buf):
    for kind, off, size, formid, flags in records(buf, 0, len(buf)):
        if kind != "QUST":
            continue
        data = buf[off:off + size]
        if flags & 0x00040000:          # compressed: 4-byte length, then zlib
            data = zlib.decompress(data[4:])
        yield formid, list(subrecords(data))


def check(buf):
    """Returns a list of problems (empty if the layout is as expected) and the number of quests seen."""
    problems = []
    quests = 0
    for formid, subs in quest_records(buf):
        quests += 1
        edid = next((d.rstrip(b"\0").decode("latin1") for t, d in subs if t == "EDID"), f"{formid:08X}")
        kinds = [t for t, _ in subs]
        if "NEXT" not in kinds:
            problems.append(f"{edid}: the NEXT marker is missing")

        # Stages run from the first INDX to the first objective, alias or end.
        stage = None            # index of the stage being read
        items = 0
        expect_flags = False    # True right after INDX
        def close_stage():
            if stage is not None and items != 1:
                problems.append(f"{edid} stage {stage}: {items} item(s); expected exactly one (a QSDT subrecord starts an item)")
        for n, (t, d) in enumerate(subs):
            if t == "INDX":
                close_stage()
                stage = struct.unpack_from("<H", d, 0)[0]
                items = 0
                expect_flags = True
                continue
            if stage is None:
                continue
            if t in ("QOBJ", "ANAM", "ALST", "ALLS", "ALCS"):
                close_stage()
                stage = None
                continue
            if t == "QSDT":
                items += 1
                expect_flags = False
                continue
            if expect_flags:
                problems.append(f"{edid} stage {stage}: {t} follows INDX; the item's flags (QSDT) must come first")
                expect_flags = False
            elif t in ITEM_PARTS and items == 0:
                problems.append(f"{edid} stage {stage}: {t} appears before any QSDT")
        close_stage()

        for n, (t, d) in enumerate(subs):
            if t != "QOBJ":
                continue
            index = struct.unpack_from("<H", d, 0)[0]
            nxt = subs[n + 1][0] if n + 1 < len(subs) else None
            if nxt != "FNAM":
                problems.append(f"{edid} objective {index}: followed by {nxt}, expected its flags (FNAM)")
    return problems, quests


def rename_nth(buf, old, new, nth):
    """Returns a copy with the nth occurrence (0-based) of a 4-byte signature replaced. Sizes are untouched."""
    pos = -1
    for _ in range(nth + 1):
        pos = buf.find(old, pos + 1)
        if pos < 0:
            return None
    return buf[:pos] + new + buf[pos + 4:]


def self_test(buf):
    """Each kind of damage must produce a problem. Returns the list of damages that went unnoticed."""
    unnoticed = []
    cases = [
        ("a stage item without its flags", b"QSDT", b"XSDT", 0),
        ("a later stage item without its flags", b"QSDT", b"XSDT", 5),
        ("no NEXT marker", b"NEXT", b"NEXX", 1),
        ("an objective without its flags", b"QOBJ\x02\x00", None, 0),
    ]
    for name, old, new, nth in cases:
        if new is None:
            # Turn the FNAM that follows the first QOBJ into something else.
            pos = buf.find(old)
            fn = buf.find(b"FNAM", pos) if pos >= 0 else -1
            damaged = None if fn < 0 or fn != pos + 8 else buf[:fn] + b"FNAX" + buf[fn + 4:]
        else:
            damaged = rename_nth(buf, old, new, nth)
        if damaged is None:
            unnoticed.append(f"{name}: could not construct the damaged file (signature not found)")
            continue
        try:
            problems, _ = check(damaged)
        except Exception as exc:          # a parse failure also counts as noticed
            problems = [str(exc)]
        if not problems:
            unnoticed.append(name)
    return unnoticed


def main(argv):
    args = [a for a in argv[1:] if a != "--self-test"]
    if len(args) != 1:
        print(__doc__)
        return 2
    buf = open(args[0], "rb").read()
    problems, quests = check(buf)
    if quests == 0:
        print(f"{args[0]}: no quest records found")
        return 1
    if problems:
        print(f"PLUGIN LAYOUT CHECK FAILED ({len(problems)}):")
        for p in problems:
            print("  " + p)
        return 1
    print(f"plugin layout: {quests} quest records; every stage has one item starting with its flags, every objective has flags, the NEXT marker is present")
    if "--self-test" in argv:
        unnoticed = self_test(buf)
        if unnoticed:
            print("LAYOUT SELF-TEST FAILED: damage that went unnoticed:")
            for u in unnoticed:
                print("  " + u)
            return 1
        print("plugin layout: 4 kinds of deliberate damage were each caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
