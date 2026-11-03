#!/usr/bin/env python3
"""Reconstructed PS1 card-format models, not a game or BIOS emulator.

Run with Python 3 standard library. Writes no files. All data are synthetic.
These tests cannot establish original-game compatibility or physical-card timing.
Source/layout: DuckStation memory_card_image.cpp; psx-spx Kernel/BIOS docs.
Game-specific constants were recovered from this conversation, not re-extracted.
"""
import hashlib
import json
import random
import struct
from functools import reduce
from operator import xor

BLOCK = 8192
FRAME = 128
CARD = 131072
FILE = 114688
NAME = b"BISLPS-00782CONV"
DATA_START = 512
DATA_LENGTH = 104360
CHECKSUM_OFFSET = DATA_START + DATA_LENGTH
PAYLOAD_END = CHECKSUM_OFFSET + 4


def checksum(frame):
    return reduce(xor, frame[:127], 0)


def seal(frame):
    frame[127] = checksum(frame)
    return frame


def format_card():
    card = bytearray([255]) * CARD
    header = bytearray(128)
    header[:2] = b"MC"
    card[:128] = seal(header)
    for i in range(1, 16):
        d = bytearray(128)
        struct.pack_into("<IIH", d, 0, 0xA0, 0, 0xFFFF)
        card[i * 128:(i + 1) * 128] = seal(d)
    for i in range(16, 36):
        d = bytearray(128)
        d[:4] = bytes([255]) * 4
        struct.pack_into("<H", d, 8, 0xFFFF)
        card[i * 128:(i + 1) * 128] = seal(d)
    card[36 * 128:63 * 128] = bytes(27 * 128)
    card[63 * 128:64 * 128] = card[:128]
    return card


def pack_file(data, chain, name=NAME):
    needed = (len(data) + BLOCK - 1) // BLOCK
    if not data or len(chain) != needed or len(set(chain)) != needed:
        raise ValueError("invalid allocation length")
    if any(b < 1 or b > 15 for b in chain) or len(name) > 20 or b"\0" in name:
        raise ValueError("invalid block/name")
    card = format_card()
    for index, block in enumerate(chain):
        d = bytearray(128)
        state = 0x51 if index == 0 else (0x53 if index == needed - 1 else 0x52)
        next_block = chain[index + 1] - 1 if index + 1 < needed else 0xFFFF
        struct.pack_into("<IIH", d, 0, state, len(data) if index == 0 else 0, next_block)
        if index == 0:
            d[10:10 + len(name)] = name
        card[block * 128:(block + 1) * 128] = seal(d)
        part = data[index * BLOCK:(index + 1) * BLOCK]
        card[block * BLOCK:block * BLOCK + len(part)] = part
    return card


def read_file(card, head):
    """Strict single-chain validator; does not audit other files or bad sectors."""
    if len(card) != CARD or card[:2] != b"MC" or checksum(card[:128]) != card[127]:
        raise ValueError("card header")
    if head < 1 or head > 15:
        raise ValueError("head")
    first = card[head * 128:(head + 1) * 128]
    size = struct.unpack_from("<I", first, 4)[0]
    if not 0 < size <= 15 * BLOCK:
        raise ValueError("size")
    count = (size + BLOCK - 1) // BLOCK
    out, seen, block = bytearray(), set(), head
    for i in range(count):
        if block < 1 or block > 15 or block in seen:
            raise ValueError("cycle or invalid block")
        seen.add(block)
        d = card[block * 128:(block + 1) * 128]
        state, _, nxt = struct.unpack_from("<IIH", d)
        expected = 0x51 if i == 0 else (0x53 if i == count - 1 else 0x52)
        if state != expected or checksum(d) != d[127]:
            raise ValueError("state or directory checksum")
        out.extend(card[block * BLOCK:(block + 1) * BLOCK])
        if i == count - 1:
            if nxt != 0xFFFF:
                raise ValueError("chain exceeds size")
        elif nxt >= 15:
            raise ValueError("short chain or invalid next")
        block = nxt + 1
    return bytes(out[:size])


def synthetic_game_file():
    data = bytearray(FILE)
    data[:4] = bytes.fromhex("53 43 13 0e")
    data[4:19] = b"SYNTHETIC TEST\0"
    data[DATA_START:CHECKSUM_OFFSET] = bytes((i * 37 + 11) & 255 for i in range(DATA_LENGTH))
    struct.pack_into("<I", data, CHECKSUM_OFFSET, sum(data[DATA_START:CHECKSUM_OFFSET]))
    data[PAYLOAD_END:] = bytes([0xA5]) * (FILE - PAYLOAD_END)
    return bytes(data)


def game_checksum_ok(data):
    return (len(data) == FILE and sum(data[DATA_START:CHECKSUM_OFFSET])
            == struct.unpack_from("<I", data, CHECKSUM_OFFSET)[0])


class Event:
    """Mode 0x2000 ready/busy latch, not a notification-counting queue."""
    def __init__(self):
        self.enabled = False
        self.ready = False

    def deliver(self):
        if self.enabled:
            self.ready = True

    def test(self):
        if self.enabled and self.ready:
            self.ready = False
            return 1
        return 0


def run():
    data = synthetic_game_file()
    assert len(data) == FILE and game_checksum_ok(data)
    layouts = 0
    for omitted in range(1, 16):
        for seed in range(12):
            chain = [b for b in range(1, 16) if b != omitted]
            random.Random(omitted * 100 + seed).shuffle(chain)
            card = pack_file(data, chain)
            assert read_file(card, chain[0]) == data
            layouts += 1

    sizes = [1, 127, 128, 129, 8191, 8192, 8193, 104364, 104876,
             114687, 114688, 114689, 122880]
    for size in sizes:
        part = bytes((i * 23) & 255 for i in range(size))
        assert read_file(pack_file(part, list(range(1, (size + BLOCK - 1) // BLOCK + 1))), 1) == part

    base = pack_file(data, list(range(1, 15)))
    bad = []
    c = base.copy()
    c[2] ^= 1
    bad.append(c)
    c = base.copy()
    c[128 + 127] ^= 1
    bad.append(c)
    # Re-seal directory changes so structural checks, not XOR alone, reject them.
    for block, offset, fmt, value in [(2, 8, "<H", 0), (1, 8, "<H", 0xFFFF),
                                     (1, 8, "<H", 15), (14, 0, "<I", 0x52),
                                     (1, 4, "<I", BLOCK)]:
        c = base.copy()
        d = c[block * 128:(block + 1) * 128]
        struct.pack_into(fmt, d, offset, value)
        c[block * 128:(block + 1) * 128] = seal(d)
        bad.append(c)
    for c in bad:
        try:
            read_file(c, 1)
        except ValueError:
            pass
        else:
            raise AssertionError("corruption accepted")

    sectors = mapped = 0
    for omitted in range(1, 16):
        for head in range(1, 16):
            if omitted == head:
                continue
            chain = [head] + [b for b in range(15, 0, -1) if b not in (omitted, head)]
            card = pack_file(data, chain)
            for logical in range(FILE // FRAME):
                index, within = divmod(logical, BLOCK // FRAME)
                physical = chain[index] * (BLOCK // FRAME) + within
                assert card[physical * FRAME:(physical + 1) * FRAME] == data[logical * FRAME:(logical + 1) * FRAME]
                sectors += 1
            mapped += 1

    mcs = bytes(base[128:256]) + data
    assert len(mcs) == 114816 and mcs[10:27] == NAME + b"\0"
    coverage = {}
    for label, offset in [("header", 0), ("payload_first", DATA_START),
                          ("payload_last", CHECKSUM_OFFSET - 1),
                          ("checksum", CHECKSUM_OFFSET), ("tail", PAYLOAD_END)]:
        changed = bytearray(data)
        changed[offset] ^= 1
        coverage[label] = game_checksum_ok(changed)
    assert coverage == dict(header=True, payload_first=False, payload_last=False,
                            checksum=False, tail=True)
    swapped = bytearray(data)
    swapped[600], swapped[601] = swapped[601], swapped[600]
    assert swapped != data and game_checksum_ok(swapped)
    assert reduce(xor, swapped[512:640], 0) == reduce(xor, data[512:640], 0)

    priority = []
    for mask in range(1, 16):
        events = [Event() for _ in range(4)]
        for i, e in enumerate(events):
            e.enabled = True
            if mask >> i & 1:
                e.deliver()
        results = []
        while any(e.ready for e in events):
            for i, e in enumerate(events):
                if e.test() == 1:
                    results.append(i)
                    break
        assert results == [i for i in range(4) if mask >> i & 1]
        priority.append(results)
    e = Event()
    e.enabled = True
    e.deliver()
    e.deliver()
    assert [e.test(), e.test()] == [1, 0]
    print(json.dumps({
        "scope": "reconstructed synthetic models; no original game execution",
        "format_checks": {"valid_chains": layouts, "size_roundtrips": len(sizes),
                          "corruptions_rejected": len(bad), "total": layouts + len(sizes) + len(bad)},
        "mapping": {"layouts": mapped, "sectors": sectors},
        "sizes": {"card": CARD, "logical_file": FILE, "mcs": len(mcs),
                  "payload_with_checksum": 104364, "retained_tail": FILE - PAYLOAD_END},
        "checksum_coverage_accepts_mutation": coverage,
        "same_sector_swap_passes_sum_and_xor": True,
        "event_priority_masks_checked": len(priority),
        "duplicate_event_deliveries_coalesce": True,
        "synthetic_file_sha256": hashlib.sha256(data).hexdigest(),
        "all_checks_passed": True
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
