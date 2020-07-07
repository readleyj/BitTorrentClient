import socket
import struct
import config
from collections import OrderedDict


class Peer:
    def __init__(self, host: int, port: int, peer_id: int = None) -> None:
        self.host = host
        self.port = port
        self.peer_id = peer_id

    @classmethod
    def from_compact(cls, data: bytes):
        host, port = struct.unpack('!4sH', data)
        host = socket.inet_ntoa(host)
        return cls(host, port)

    @classmethod
    def from_dict(cls, info_dict: OrderedDict):
        pass

    def __str__(self):
        return 'Peer IP: {} \n' \
               'Peer Port: {}'.format(self.host, self.port)


class Handshake:
    def __init__(self, info_hash: bytes, peer_id: bytes) -> None:
        self.info_hash = info_hash

        if isinstance(peer_id, str):
            peer_id = peer_id.encode('utf-8')

        self.peer_id = peer_id

        print(self.info_hash)

    def encode(self) -> None:
        return struct.pack(
            '>B19s8x20s20s',
            config.pstrlen,
            config.pstr,
            self.info_hash,
            self.peer_id
        )

    @classmethod
    def from_packed(cls, data: bytes):
        parts = struct.unpack('>B19s8x20s20s', data)

        if parts[0] != config.pstrlen or parts[1] != config.pstr:
            return None

        return cls(info_hash=parts[2], peer_id=parts[3])


class Block:
    MISSING = 0
    PENDING = 1
    RETRIEVED = 2

    def __init__(self, piece, offset, length):
        self.piece = piece
        self.offset = offset
        self.length = length
        self.status = Block.MISSING
        self.data = None

