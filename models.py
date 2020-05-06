import socket
import struct
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