"""Bounded raw PS1 card filesystem model, NOT BIOS/SIO emulation.

Format reference: https://psx-spx.consoledev.net/dev/ps1/sio/controllersandmemorycards/memory-card-data-format/
Only fresh free blocks and active files are supported. Corruption rejection is
this model's policy; it makes no claim about original BIOS recovery behavior.
"""
import struct
from collections.abc import MutableMapping
from functools import reduce
from operator import xor

FRAME, BLOCK, TOTAL = 128, 8192, 131072


def frame_checksum(data):
    return reduce(xor, data[:127], 0)


class RawCard:
    def __init__(self, image=None, allocation_order=range(1, 16)):
        self.order = list(allocation_order)
        if sorted(self.order) != list(range(1, 16)):
            raise ValueError('allocation order must permute all 15 data blocks')
        self.image = bytearray(image) if image is not None else self.format()
        self.transfers = []
        self.validate()

    @staticmethod
    def format():
        data = bytearray(b'\xff' * TOTAL)
        def frame(n, body):
            record = bytearray(body.ljust(127, b'\0'))
            assert len(record) == 127
            record.append(frame_checksum(record))
            data[n*FRAME:(n+1)*FRAME] = record
        frame(0, b'MC')
        for n in range(1, 16):
            frame(n, struct.pack('<IIH', 0xa0, 0, 0xffff))
        for n in range(16, 36):
            frame(n, b'\xff'*4)
        data[63*FRAME:64*FRAME] = data[:FRAME]
        return data

    @staticmethod
    def filename(path):
        if not isinstance(path, bytes) or not path.startswith(b'bu00:'):
            raise ValueError('only bu00: ASCII paths are modeled')
        name = path[5:]
        if not 1 <= len(name) <= 20 or b'\0' in name or any(b > 127 for b in name):
            raise ValueError('invalid filename')
        return name

    def entry(self, block):
        return self.image[block*FRAME:(block+1)*FRAME]

    def state(self, block):
        return struct.unpack_from('<I', self.entry(block))[0]

    def directory(self):
        result = {}
        for first in range(1, 16):
            entry = self.entry(first)
            if self.state(first) != 0x51:
                continue
            name = bytes(entry[10:31]).split(b'\0', 1)[0]
            path = b'bu00:' + name
            self.filename(path)
            if path in result:
                raise ValueError('duplicate filename')
            chain, current = [], first
            while True:
                if not 1 <= current <= 15 or current in chain:
                    raise ValueError('invalid or cyclic chain')
                record = self.entry(current)
                state, size, nxt = struct.unpack_from('<IIH', record)
                expected = 0x51 if not chain else (0x53 if nxt == 0xffff else 0x52)
                if state != expected:
                    raise ValueError('allocation state does not match chain')
                if chain and (size or any(record[10:31])):
                    raise ValueError('continuation metadata is not empty')
                chain.append(current)
                if nxt == 0xffff:
                    break
                current = nxt + 1
            size = struct.unpack_from('<I', entry, 4)[0]
            if size != len(chain)*BLOCK:
                raise ValueError('size does not match block chain')
            result[path] = dict(size=size, blocks=chain)
        return result

    def validate(self):
        if len(self.image) != TOTAL or self.image[:2] != b'MC':
            raise ValueError('invalid card size or header')
        for n in range(36):
            frame = self.image[n*FRAME:(n+1)*FRAME]
            if frame_checksum(frame) != frame[127]:
                raise ValueError('system frame checksum mismatch')
        if any(self.image[n*FRAME:n*FRAME+4] != b'\xff'*4 for n in range(16, 36)):
            raise ValueError('bad-sector remapping is not modeled')
        entries = self.directory()
        occupied = [block for item in entries.values() for block in item['blocks']]
        if len(set(occupied)) != len(occupied):
            raise ValueError('cross-linked files')
        for block in range(1, 16):
            if block not in occupied and self.state(block) != 0xa0:
                raise ValueError('orphan, deleted, or unsupported block state')
        return entries

    def create(self, path, data):
        name = self.filename(path)
        entries = self.validate()
        if path in entries:
            raise ValueError('file already exists')
        if not data or len(data) % BLOCK:
            raise ValueError('file size must be a positive block multiple')
        count = len(data)//BLOCK
        free = [n for n in self.order if self.state(n) == 0xa0]
        if count > len(free):
            raise ValueError('insufficient free blocks')
        blocks = free[:count]
        for index, block in enumerate(blocks):
            record = bytearray(FRAME)
            state = 0x51 if index == 0 else (0x53 if index == count-1 else 0x52)
            nxt = blocks[index+1]-1 if index+1 < count else 0xffff
            struct.pack_into('<IIH', record, 0, state, len(data) if index == 0 else 0, nxt)
            if index == 0:
                record[10:10+len(name)] = name
            record[127] = frame_checksum(record)
            self.image[block*FRAME:(block+1)*FRAME] = record
            self.image[block*BLOCK:(block+1)*BLOCK] = data[index*BLOCK:(index+1)*BLOCK]
        self.validate()

    def segments(self, path, start, size):
        item = self.directory()[path]
        if start < 0 or size < 0 or start+size > item['size']:
            raise ValueError('file bounds')
        while size:
            index, inner = divmod(start, BLOCK)
            block = item['blocks'][index]
            length = min(size, BLOCK-inner)
            yield dict(logical=start, physical=block*BLOCK+inner, block=block, size=length)
            start += length
            size -= length

    def read(self, path, start, size, trace=True):
        parts = list(self.segments(path, start, size))
        if trace:
            self.transfers.append(dict(op='read', path=path.decode(), offset=start, size=size, segments=parts))
        return b''.join(bytes(self.image[p['physical']:p['physical']+p['size']]) for p in parts)

    def write(self, path, start, data):
        parts = list(self.segments(path, start, len(data)))
        self.transfers.append(dict(op='write', path=path.decode(), offset=start, size=len(data), segments=parts))
        offset = 0
        for part in parts:
            p, size = part['physical'], part['size']
            self.image[p:p+size] = data[offset:offset+size]
            offset += size


class CardFileBuffer:
    def __init__(self, card, path):
        self.card, self.path = card, path

    def __len__(self):
        return self.card.directory()[self.path]['size']

    def __bytes__(self):
        return self.card.read(self.path, 0, len(self), trace=False)

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise TypeError('only file slices are supported')
        start, stop, step = key.indices(len(self))
        if step != 1:
            raise ValueError('non-unit slice')
        return self.card.read(self.path, start, max(0, stop-start))

    def __setitem__(self, key, data):
        start, stop, step = key.indices(len(self))
        if step != 1 or len(data) != stop-start:
            raise ValueError('file resize or non-unit slice')
        self.card.write(self.path, start, bytes(data))


class CardFiles(MutableMapping):
    def __init__(self, card):
        self.card = card

    def __getitem__(self, path):
        if path not in self.card.directory():
            raise KeyError(path)
        return CardFileBuffer(self.card, path)

    def __setitem__(self, path, data):
        self.card.create(path, bytes(data))

    def __iter__(self):
        return iter(self.card.directory())

    def __len__(self):
        return len(self.card.directory())

    def __delitem__(self, path):
        raise NotImplementedError('deletion/recovery is outside this bounded model')
