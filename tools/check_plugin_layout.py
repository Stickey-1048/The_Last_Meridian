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

What it asserts where the plugin places references in a cell of the game
(none in a plugin built without the game's master file):
  - the cell's record is filed where an interior cell belongs: under the block
    numbered by the last decimal digit of its id and the sub-block numbered by
    the digit before it, with its references in a group of their own under it;
  - the cell is one of a master's, and every reference under it is one of this
    plugin's: the game's own references are not copied;
  - every reference is a placed actor or object (ACHR, REFR) with a base (NAME)
    and a position (DATA, 24 bytes); it is flagged persistent exactly when it
    is in the cell's persistent group; a box (XPRM) is 32 bytes; where its
    reach is in the file a second time, as the reference's bound (XMBO), the
    two are the same three numbers (the format notes for the game before this
    one say the editor refuses a box where they differ);
  - a base (NAME) is a record of a master the plugin names, or one of the
    plugin's own that is in the file;
  - a quest alias that is filled with a reference of this plugin (ALFR)
    points at one that is under a cell in the file;
  - and, read beside the description the builder wrote (TheLastMeridian.json
    in the same folder): which kind of reference it is, its name, its base,
    position and rotation, the shape and sizes of its box as the file holds
    them, the collision layer and the "initially disabled" flag are what it
    says. The description is read back through the library; this reads the
    bytes.

What it asserts for every actor (NPC_) record of the plugin's own (none in a
plugin built without the game's master file: they are copies of the game's):
  - it has nothing to go about: no package (PKID) and no script (VMAD), and
    its template flags (in ACBS) do not fetch either from the actor it is
    modelled on. That is what the builder means such an actor to be; a
    placed person with packages did not stay where it was put (2026-11-13);
  - and, read beside the builder's description: the actors in the file are
    the ones it lists, each with the default package list (DPLT) and the
    template flags it says.

The layout is the one in xEdit's record definitions for Fallout 4
(wbDefinitionsFO4.pas, records QUST, CELL, REFR, ACHR, NPC_, and the group types).
It is a check of the file's shape. It does not prove what the game does with it.

Usage:  check_plugin_layout.py <plugin.esp>     exit 0 if the layout is as expected
        check_plugin_layout.py --self-test <plugin.esp>
            also damages copies of the file in memory and requires each kind
            of damage to be caught
"""
import json
import os
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


# ------------------------------------------------------------------ cells

GROUP_TOP, GROUP_CELL_BLOCK, GROUP_CELL_SUBBLOCK = 0, 2, 3
GROUP_CELL_CHILDREN, GROUP_CELL_PERSISTENT, GROUP_CELL_TEMPORARY = 6, 8, 9
PERSISTENT, INITIALLY_DISABLED, COMPRESSED = 0x400, 0x800, 0x00040000


def items(buf, start, end):
    """Yields what lies directly between start and end: ('group', type, label bytes, start of content, end)
    or ('record', type, FormID, flags, data bytes)."""
    i = start
    while i < end:
        kind = buf[i:i + 4].decode("latin1")
        if kind == "GRUP":
            size, label, gtype = struct.unpack_from("<I4sI", buf, i + 4)
            if size < 24 or i + size > end:
                raise ValueError(f"group at {i} has size {size}")
            yield "group", gtype, label, i + 24, i + size
            i += size
        else:
            size, flags, formid = struct.unpack_from("<III", buf, i + 4)
            data = buf[i + 24:i + 24 + size]
            if flags & COMPRESSED:
                data = zlib.decompress(data[4:])
            yield "record", kind, formid, flags, data
            i += 24 + size


def master_count(buf):
    for item in items(buf, 0, len(buf)):
        if item[0] == "record" and item[1] == "TES4":
            return sum(1 for t, _ in subrecords(item[4]) if t == "MAST")
        break
    raise ValueError("the file does not begin with a TES4 record")


SHAPES = {1: "Box", 2: "Sphere", 3: "Plane", 4: "Line", 5: "Ellipsoid"}
KINDS = {"ACHR": "PlacedNpc", "REFR": "PlacedObject"}


def placed_from_json(path):
    """FormID -> what the builder's description says about each placed reference, or None without the file.
    Each entry also gets "BaseId": the FormID its base should have in the file, with the plugin's own
    records numbered after its masters (None if the description names a record it does not list)."""
    if not os.path.exists(path):
        return None
    data = json.load(open(path, encoding="utf-8-sig"))
    masters = [m.lower() for m in data.get("Masters", [])]
    own = {}
    for group in ("Records", "Messages", "Quests"):
        for rec in data.get(group, []):
            own[rec["EditorId"]] = int(rec["FormKey"].split(":")[0], 16)
    out = {}
    for cell in data.get("Cells", []):
        for p in cell["Placed"]:
            base = p["Base"]
            if ":" in base:
                number, _, file = base.partition(":")
                p["BaseId"] = (masters.index(file.lower()) << 24 | int(number, 16)) if file.lower() in masters else None
            else:
                p["BaseId"] = (len(masters) << 24 | own[base]) if base in own else None
            out[int(p["FormKey"].split(":")[0], 16)] = p
    return out


# The bits of an actor's "use template actors" flags, a 16-bit number 14 bytes into ACBS.
TEMPLATE_FLAGS = ["Traits", "Stats", "Factions", "SpellList", "AiData", "AiPackages", "ModelOrAnimation", "BaseData",
                  "Inventory", "Script", "DefPackList", "AttackData", "Keywords"]
ACBS_SIZE, ACBS_TEMPLATE_AT = 20, 14


def npcs_from_json(path):
    """EditorID -> what the builder's description says about each actor of the plugin's own, or None without the file."""
    if not os.path.exists(path):
        return None
    data = json.load(open(path, encoding="utf-8-sig"))
    return {n["EditorId"]: n for n in data.get("Npcs", [])}


def check_npcs(buf, described=None):
    """Returns (problems, number of actor records of the plugin's own)."""
    problems = []
    masters = master_count(buf)
    seen = set()
    for kind, off, size, formid, flags in records(buf, 0, len(buf)):
        if kind != "NPC_":
            continue
        if formid >> 24 != masters:
            problems.append(f"actor {formid:08X}: a record of a master's; this plugin changes none of the game's actors")
            continue
        data = buf[off:off + size]
        if flags & 0x00040000:
            data = zlib.decompress(data[4:])
        subs = list(subrecords(data))
        names = [d for t, d in subs if t == "EDID"]
        edid = names[0].rstrip(b"\0").decode("latin1") if names else f"{formid:08X}"
        seen.add(edid)
        kinds = [t for t, _ in subs]
        if "PKID" in kinds:
            problems.append(f"actor {edid}: has {kinds.count('PKID')} package(s)")
        if "VMAD" in kinds:
            problems.append(f"actor {edid}: has scripts attached")
        acbs = [d for t, d in subs if t == "ACBS"]
        template = None
        if len(acbs) != 1 or len(acbs[0]) != ACBS_SIZE:
            problems.append(f"actor {edid}: its base data (ACBS) is {'missing' if not acbs else 'not %d bytes' % ACBS_SIZE}")
        else:
            bits = struct.unpack_from("<H", acbs[0], ACBS_TEMPLATE_AT)[0]
            template = {name for i, name in enumerate(TEMPLATE_FLAGS) if bits >> i & 1}
            if bits >> len(TEMPLATE_FLAGS):
                problems.append(f"actor {edid}: template flags {bits:#06x} hold a bit this check has no name for")
            for name in ("AiPackages", "Script"):
                if name in template:
                    problems.append(f"actor {edid}: takes {name} from the actor it is modelled on")
        if described is None:
            continue
        want = described.get(edid)
        if want is None:
            problems.append(f"actor {edid}: in the file, and not in the builder's description")
            continue
        if want["Packages"] != 0 or want["Scripts"]:
            problems.append(f"actor {edid}: the builder's description gives it {want['Packages']} package(s) and scripts {want['Scripts']}")
        if ("DPLT" in kinds) != want["HasDefaultPackageList"]:
            problems.append(f"actor {edid}: {'has a' if 'DPLT' in kinds else 'has no'} default package list; the builder's description says otherwise")
        if template is not None and template != set(want["TemplateFlags"]):
            problems.append(f"actor {edid}: template flags {sorted(template)}; the builder's description says {sorted(want['TemplateFlags'])}")
    if described is not None:
        for edid in sorted(set(described) - seen):
            problems.append(f"actor {edid}: in the builder's description, and not in the file")
    return problems, len(seen)


def own_record_ids(buf, masters):
    """The FormIDs of every record in the file that is the plugin's own."""
    return {formid for kind, _off, _size, formid, _flags in records(buf, 0, len(buf)) if kind != "TES4" and formid >> 24 == masters}


def check_cells(buf, described=None):
    """Returns (problems, number of cell records, number of references under them)."""
    problems = []
    masters = master_count(buf)
    own = own_record_ids(buf, masters)
    cells = refs = 0
    seen = set()
    for item in items(buf, 0, len(buf)):
        if item[0] != "group" or item[1] != GROUP_TOP or item[2] != b"CELL":
            continue
        for block in items(buf, item[3], item[4]):
            if block[0] != "group" or block[1] != GROUP_CELL_BLOCK:
                problems.append(f"the CELL group holds something that is not an interior cell block: {block[:3]}")
                continue
            block_number = struct.unpack("<i", block[2])[0]
            for sub in items(buf, block[3], block[4]):
                if sub[0] != "group" or sub[1] != GROUP_CELL_SUBBLOCK:
                    problems.append(f"cell block {block_number} holds something that is not a sub-block: {sub[:3]}")
                    continue
                sub_number = struct.unpack("<i", sub[2])[0]
                cell = None
                for thing in items(buf, sub[3], sub[4]):
                    if thing[0] == "record":
                        if thing[1] != "CELL":
                            problems.append(f"cell sub-block {block_number}/{sub_number} holds a {thing[1]} record")
                            cell = None
                            continue
                        cell = thing[2]
                        cells += 1
                        name = f"cell {cell:08X}"
                        object_id = cell & 0xFFFFFF
                        if (block_number, sub_number) != (object_id % 10, object_id // 10 % 10):
                            problems.append(f"{name}: filed under block {block_number}, sub-block {sub_number}; "
                                            f"its id asks for {object_id % 10} and {object_id // 10 % 10}")
                        if cell >> 24 >= masters:
                            problems.append(f"{name}: is a new cell of this plugin; only copies of a master's cells are expected")
                        continue
                    if thing[1] != GROUP_CELL_CHILDREN or cell is None or struct.unpack("<I", thing[2])[0] != cell:
                        problems.append(f"cell sub-block {block_number}/{sub_number}: a group of type {thing[1]} that does not belong to the cell record before it")
                        continue
                    name = f"cell {cell:08X}"
                    for part in items(buf, thing[3], thing[4]):
                        if part[0] != "group" or part[1] not in (GROUP_CELL_PERSISTENT, GROUP_CELL_TEMPORARY):
                            problems.append(f"{name}: its group holds something that is neither its persistent nor its temporary references: {part[:3]}")
                            continue
                        if struct.unpack("<I", part[2])[0] != cell:
                            problems.append(f"{name}: a group of references labelled for another cell")
                        in_persistent = part[1] == GROUP_CELL_PERSISTENT
                        for ref in items(buf, part[3], part[4]):
                            if ref[0] != "record":
                                problems.append(f"{name}: a group inside its list of references")
                                continue
                            _, kind, formid, flags, data = ref
                            refs += 1
                            seen.add(formid)
                            who = f"{kind} {formid:08X}"
                            if kind not in ("ACHR", "REFR"):
                                problems.append(f"{name}: holds a {kind} record")
                                continue
                            if formid >> 24 != masters:
                                problems.append(f"{who}: is not a reference of this plugin (a master's reference copied into the plugin would replace it)")
                            if bool(flags & PERSISTENT) != in_persistent:
                                problems.append(f"{who}: flagged {'persistent' if flags & PERSISTENT else 'temporary'} "
                                                f"but in the cell's {'persistent' if in_persistent else 'temporary'} group")
                            subs = dict(subrecords(data))
                            base = struct.unpack("<I", subs["NAME"])[0] if len(subs.get("NAME", b"")) == 4 else None
                            if base is None:
                                problems.append(f"{who}: no base (NAME)")
                            elif base >> 24 > masters:
                                problems.append(f"{who}: its base {base:08X} belongs to a file the plugin does not name as a master")
                            elif base >> 24 == masters and base not in own:
                                problems.append(f"{who}: its base {base:08X} would be a record of this plugin, and the file has none with that id")
                            if len(subs.get("DATA", b"")) != 24:
                                problems.append(f"{who}: position and rotation (DATA) are {len(subs.get('DATA', b''))} bytes, expected 24")
                                continue
                            box = None
                            if "XPRM" in subs:
                                if len(subs["XPRM"]) != 32:
                                    problems.append(f"{who}: the primitive (XPRM) is {len(subs['XPRM'])} bytes, expected 32")
                                else:
                                    box = struct.unpack_from("<3f", subs["XPRM"], 0)
                                    shape = struct.unpack_from("<I", subs["XPRM"], 28)[0]
                                    if shape not in (1, 2, 3, 4, 5):
                                        problems.append(f"{who}: the primitive has the unknown shape {shape}")
                                    if "XMBO" in subs:
                                        if len(subs["XMBO"]) != 12:
                                            problems.append(f"{who}: the bound (XMBO) is {len(subs['XMBO'])} bytes, expected 12")
                                        elif any(abs(a - b) > 0.001 for a, b in zip(struct.unpack("<3f", subs["XMBO"]), box)):
                                            problems.append(f"{who}: the bound {struct.unpack('<3f', subs['XMBO'])} is not the box's reach {box}")
                            if "XTRI" in subs and len(subs["XTRI"]) != 4:
                                problems.append(f"{who}: the collision layer (XTRI) is {len(subs['XTRI'])} bytes, expected 4")
                            if described is None:
                                continue
                            want = described.get(formid & 0xFFFFFF)
                            if want is None:
                                problems.append(f"{who}: not in the builder's description of the plugin")
                                continue
                            if KINDS[kind] != want["Kind"]:
                                problems.append(f"{who}: a {KINDS[kind]} in the file, a {want['Kind']} in the description")
                            name = subs.get("EDID", b"").rstrip(b"\0").decode("latin1") or None
                            if name != want["EditorId"]:
                                problems.append(f"{who}: named {name} in the file, {want['EditorId']} in the description")
                            if base is not None and base != want["BaseId"]:
                                problems.append(f"{who}: its base is {base:08X} in the file, {want['Base']} in the description")
                            position = struct.unpack_from("<3f", subs["DATA"], 0)
                            if any(abs(a - b) > 0.001 for a, b in zip(position, want["Position"])):
                                problems.append(f"{who}: at {position} in the file, {want['Position']} in the description")
                            rotation = struct.unpack_from("<3f", subs["DATA"], 12)
                            if any(abs(a - b) > 0.0001 for a, b in zip(rotation, want["Rotation"])):
                                problems.append(f"{who}: turned {rotation} in the file, {want['Rotation']} in the description")
                            shape = SHAPES.get(struct.unpack_from("<I", subs["XPRM"], 28)[0]) if len(subs.get("XPRM", b"")) == 32 else None
                            if shape != want["Primitive"]:
                                problems.append(f"{who}: its primitive is {shape} in the file, {want['Primitive']} in the description")
                            if bool(flags & INITIALLY_DISABLED) != want["InitiallyDisabled"]:
                                problems.append(f"{who}: 'initially disabled' is {bool(flags & INITIALLY_DISABLED)} in the file, {want['InitiallyDisabled']} in the description")
                            if (box is None) != (want["Box"] is None) or (box and any(abs(a - b) > 0.001 for a, b in zip(box, want["Box"]))):
                                problems.append(f"{who}: the box is {box} in the file, {want['Box']} in the description")
                            if ("XMBO" in subs) != (want.get("Bound") is not None):
                                problems.append(f"{who}: the bound is {'in' if 'XMBO' in subs else 'not in'} the file, and {'in' if want.get('Bound') is not None else 'not in'} the description")
                            layer = struct.unpack("<I", subs["XTRI"])[0] if len(subs.get("XTRI", b"")) == 4 else None
                            if layer != want["CollisionLayer"]:
                                problems.append(f"{who}: collision layer {layer} in the file, {want['CollisionLayer']} in the description")
    if described is not None:
        for formid, want in described.items():
            if not any(s & 0xFFFFFF == formid for s in seen):
                problems.append(f"{want['EditorId']}: in the builder's description, but not under any cell in the file")
    # A quest alias filled with a reference of this plugin must point at one that is in the file.
    for formid, subs in quest_records(buf):
        edid = next((d.rstrip(b"\0").decode("latin1") for t, d in subs if t == "EDID"), f"{formid:08X}")
        for t, d in subs:
            if t == "ALFR" and len(d) == 4:
                target = struct.unpack("<I", d)[0]
                if target >> 24 == masters and target not in seen:
                    problems.append(f"{edid}: an alias is filled with the reference {target:08X}, which is not under any cell in the file")
                elif target >> 24 > masters:
                    problems.append(f"{edid}: an alias is filled with the reference {target:08X}, of a file the plugin does not name as a master")
    return problems, cells, refs


def rename_nth(buf, old, new, nth):
    """Returns a copy with the nth occurrence (0-based) of a 4-byte signature replaced. Sizes are untouched."""
    pos = -1
    for _ in range(nth + 1):
        pos = buf.find(old, pos + 1)
        if pos < 0:
            return None
    return buf[:pos] + new + buf[pos + 4:]


def find_group(buf, gtype):
    """Offset of the first group of that type, or -1. Groups are found by walking the file, not by searching bytes."""
    def walk(start, end):
        i = start
        while i < end:
            if buf[i:i + 4] == b"GRUP":
                size, _label, kind = struct.unpack_from("<I4sI", buf, i + 4)
                if kind == gtype:
                    return i
                found = walk(i + 24, i + size)
                if found >= 0:
                    return found
                i += size
            else:
                i += 24 + struct.unpack_from("<I", buf, i + 4)[0]
        return -1
    return walk(0, len(buf))


def first_ref(buf, kind=None, with_sub=None):
    """Offset of the first reference record under a cell (optionally of one kind, or having one subrecord), or -1."""
    for gtype in (GROUP_CELL_PERSISTENT, GROUP_CELL_TEMPORARY):
        g = find_group(buf, gtype)
        if g < 0:
            continue
        size = struct.unpack_from("<I", buf, g + 4)[0]
        i = g + 24
        while i < g + size:
            rec_size = struct.unpack_from("<I", buf, i + 4)[0]
            if (kind is None or buf[i:i + 4] == kind) and (with_sub is None or with_sub in buf[i + 24:i + 24 + rec_size]):
                return i
            i += 24 + rec_size
    return -1


def patch(buf, offset, new):
    return buf[:offset] + new + buf[offset + len(new):]


def cell_damage(buf):
    """(name, damaged copy or None) for each kind of damage to the cells part. Sizes are never changed."""
    out = []
    g = find_group(buf, GROUP_CELL_BLOCK)
    label = struct.unpack_from("<i", buf, g + 8)[0] if g >= 0 else 0
    out.append(("a cell filed under the wrong block", None if g < 0 else patch(buf, g + 8, struct.pack("<i", (label + 1) % 10))))
    g = find_group(buf, GROUP_CELL_PERSISTENT)
    out.append(("persistent references in the temporary group", None if g < 0 else patch(buf, g + 12, struct.pack("<I", GROUP_CELL_TEMPORARY))))
    r = first_ref(buf)
    flags = struct.unpack_from("<I", buf, r + 8)[0] if r >= 0 else 0
    out.append(("a reference in the persistent group without the persistent flag", None if r < 0 else patch(buf, r + 8, struct.pack("<I", flags & ~PERSISTENT))))
    out.append(("a reference that belongs to the master", None if r < 0 else patch(buf, r + 15, b"\x00")))
    out.append(("a reference whose 'initially disabled' flag was flipped", None if r < 0 else patch(buf, r + 8, struct.pack("<I", flags ^ INITIALLY_DISABLED))))
    if r >= 0:
        size = struct.unpack_from("<I", buf, r + 4)[0]
        n = buf.find(b"NAME", r + 24, r + 24 + size)
        out.append(("a reference whose base is of a file that is no master", None if n < 0 else patch(buf, n + 9, b"\x05")))
        out.append(("a reference with another base", None if n < 0 else patch(buf, n + 6, struct.pack("<I", struct.unpack_from("<I", buf, n + 6)[0] ^ 1))))
        e = buf.find(b"EDID", r + 24, r + 24 + size)
        out.append(("a reference with another name", None if e < 0 else patch(buf, e + 6, b"X")))
        d = buf.find(b"DATA", r + 24, r + 24 + size)
        out.append(("a reference turned another way", None if d < 0 else patch(buf, d + 6 + 20, struct.pack("<f", struct.unpack_from("<f", buf, d + 6 + 20)[0] + 0.5))))
    a = buf.find(b"ALFR\x04\x00")
    while a >= 0 and buf[a + 9] == 0:           # skip aliases filled with a master's reference (the player)
        a = buf.find(b"ALFR\x04\x00", a + 1)
    out.append(("an alias filled with a reference that is not in the file", None if a < 0 else patch(buf, a + 6, struct.pack("<I", struct.unpack_from("<I", buf, a + 6)[0] + 0x400))))
    r = first_ref(buf, with_sub=b"XPRM")
    if r < 0:
        out.append(("a box of another size", None))
        out.append(("a reference moved", None))
    else:
        size = struct.unpack_from("<I", buf, r + 4)[0]
        x = buf.find(b"XPRM", r + 24, r + 24 + size)
        out.append(("a box of another size", patch(buf, x + 6, struct.pack("<f", struct.unpack_from("<f", buf, x + 6)[0] / 2))))
        out.append(("a box turned into a sphere", patch(buf, x + 6 + 28, struct.pack("<I", 2))))
        b = buf.find(b"XMBO", r + 24, r + 24 + size)
        if b >= 0:      # a build that follows a master whose own triggers have no bound writes none
            out.append(("a box whose bound says another size", patch(buf, b + 6, struct.pack("<f", struct.unpack_from("<f", buf, b + 6)[0] + 1))))
            out.append(("a box without the bound its description has", patch(buf, b, b"XMBX")))
        x = buf.find(b"XTRI", r + 24, r + 24 + size)
        if x >= 0:      # a build against a master without collision layers has none to lose
            out.append(("a trigger without its collision layer", patch(buf, x, b"XTRX")))
        x = buf.find(b"DATA", r + 24, r + 24 + size)
        out.append(("a reference moved", None if x < 0 else patch(buf, x + 6, struct.pack("<f", struct.unpack_from("<f", buf, x + 6)[0] + 10))))
    return out


def first_own_npc(buf, with_sub=None):
    """(offset of the record, its size) for the first actor of the plugin's own (optionally one having a subrecord), or (-1, 0)."""
    masters = master_count(buf)
    for kind, off, size, formid, flags in records(buf, 0, len(buf)):
        if kind == "NPC_" and formid >> 24 == masters and not flags & 0x00040000 and (with_sub is None or with_sub in buf[off:off + size]):
            return off - 24, size
    return -1, 0


def npc_damage(buf):
    """(name, damaged copy or None) for each kind of damage to the actors part. Sizes are never changed."""
    out = []
    r, size = first_own_npc(buf)
    a = buf.find(b"ACBS", r + 24, r + 24 + size) if r >= 0 else -1
    at = a + 6 + ACBS_TEMPLATE_AT
    bits = struct.unpack_from("<H", buf, at)[0] if a >= 0 else 0
    out.append(("an actor that takes its packages from a template", None if a < 0 else patch(buf, at, struct.pack("<H", bits | 0x20))))
    out.append(("an actor that takes its scripts from a template", None if a < 0 else patch(buf, at, struct.pack("<H", bits | 0x200))))
    out.append(("an actor with another template flag", None if a < 0 else patch(buf, at, struct.pack("<H", bits ^ 0x2))))
    # A package: any subrecord that holds one FormID will do for the shape of it.
    f = buf.find(b"RNAM\x04\x00", r + 24, r + 24 + size) if r >= 0 else -1
    out.append(("an actor with a package", None if f < 0 else patch(buf, f, b"PKID")))
    e = buf.find(b"EDID", r + 24, r + 24 + size) if r >= 0 else -1
    out.append(("an actor under another name", None if e < 0 else patch(buf, e + 6, b"X")))
    r, size = first_own_npc(buf, b"DPLT")
    d = buf.find(b"DPLT", r + 24, r + 24 + size) if r >= 0 else -1
    if d >= 0:      # a build against a master whose settler names no default package list has none to lose
        out.append(("an actor without the default package list its description has", patch(buf, d, b"DPLX")))
    return out


def self_test(buf, described=None, cells=0, npcs=0, described_npcs=None):
    """Each kind of damage must produce a problem. Returns the list of damages that went unnoticed, and how many kinds were tried."""
    unnoticed = []
    tried = 0
    if npcs:
        for name, damaged in npc_damage(buf):
            tried += 1
            if damaged is None:
                unnoticed.append(f"{name}: could not construct the damaged file")
                continue
            try:
                problems, _ = check_npcs(damaged, described_npcs)
            except Exception as exc:
                problems = [str(exc)]
            if not problems:
                unnoticed.append(name)
    if cells:
        for name, damaged in cell_damage(buf):
            tried += 1
            if damaged is None:
                unnoticed.append(f"{name}: could not construct the damaged file")
                continue
            try:
                problems, _, _ = check_cells(damaged, described)
            except Exception as exc:
                problems = [str(exc)]
            if not problems:
                unnoticed.append(name)
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
        tried += 1
        try:
            problems, _ = check(damaged)
        except Exception as exc:          # a parse failure also counts as noticed
            problems = [str(exc)]
        if not problems:
            unnoticed.append(name)
    return unnoticed, tried


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
    described = placed_from_json(os.path.splitext(args[0])[0] + ".json")
    cell_problems, cells, refs = check_cells(buf, described)
    problems += cell_problems
    described_npcs = npcs_from_json(os.path.splitext(args[0])[0] + ".json")
    npc_problems, npcs = check_npcs(buf, described_npcs)
    problems += npc_problems
    if problems:
        print(f"PLUGIN LAYOUT CHECK FAILED ({len(problems)}):")
        for p in problems:
            print("  " + p)
        return 1
    print(f"plugin layout: {quests} quest records; every stage has one item starting with its flags, every objective has flags, the NEXT marker is present")
    if cells:
        beside = "and agrees with the builder's description" if described is not None else "(no description beside the plugin to compare with)"
        print(f"plugin layout: {refs} placed references under {cells} cell record(s) of the game; each is this plugin's own, filed and flagged as it should be, {beside}")
    else:
        print("plugin layout: no cell records (nothing is placed in the world by this build)")
    if npcs:
        beside = "and each is as the builder's description says" if described_npcs is not None else "(no description beside the plugin to compare with)"
        print(f"plugin layout: {npcs} actor record(s) of the plugin's own; none has a package or a script, or takes either from a template, {beside}")
    else:
        print("plugin layout: no actor records (this build makes none)")
    if "--self-test" in argv:
        unnoticed, tried = self_test(buf, described, cells, npcs, described_npcs)
        if unnoticed:
            print("LAYOUT SELF-TEST FAILED: damage that went unnoticed:")
            for u in unnoticed:
                print("  " + u)
            return 1
        print(f"plugin layout: {tried} kinds of deliberate damage were each caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
