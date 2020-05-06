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
    def from_compact(cls, data: bytes) -> Peer:
        host, port = struct.unpack('!4sH', data)
        host = socket.inet_ntoa(host)
        return cls(host, port)

    @classmethod
    def from_dict(cls, info_dict: OrderedDict) -> Peer:
        pass


class Handshake:
    def __init__(self, info_hash: bytes, peer_id: int) -> None:
        self.info_hash = info_hash
        self.peer_id = peer_id

    def encode(self) -> None:
        return struct.pack(
            '>B19s8x20s20s',
            config.pstrlen,
            config.pstr,
            self.info_hash,
            self.peer_id.encode('utf-8')
        )

    @classmethod
    def from_packed(cls, data: bytes) -> Handshake:
        parts = struct.unpack('>B19s8x20s20s', data)
        return cls(info_hash=parts[2], peer_id=parts[3])
