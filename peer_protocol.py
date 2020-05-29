import asyncio
import config
from enum import Enum
from models import Handshake


class MessageType(Enum):
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9


class PeerConnection:
    def __init__(self, peer_queue: asyncio.Queue, client_id: int, info_hash: bytes) -> None:
        self.client_id = client_id
        self.remote_id = None
        self.info_hash = info_hash

        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.connected = False

        self.peer_queue = peer_queue
        self.reader = None
        self.writer = None

    async def run(self):
        await self.connect()

    async def connect(self):
        peer = await self.peer_queue.get()
        self.reader, self.writer = await asyncio.open_connection(peer.host, peer.port)
        await self.send_handshake()
        await self.receive_handshake()

    async def send_handshake(self):
        handshake = Handshake(self.info_hash, self.client_id)
        self.writer.write(handshake.encode())
        await self.writer.drain()

    async def receive_handshake(self):
        response = await asyncio.wait_for(self.reader.readexactly(config.HANDSHAKE_LENGTH), config.READ_TIMEOUT)

        if not response:
            raise ProtocolError('Could not receive handshake')

        handshake = Handshake.from_packed(response)

        if not handshake:
            raise ProtocolError('Unknown protocol')

        if not handshake.info_hash == self.info_hash:
            raise ProtocolError('Received handshake with invalid info hash')

        self.remote_id = handshake.peer_id
        self.connected = True
        print('ID of remote peer is {}'.format(self.remote_id))

    async def receive_message(self):
        max_len = config.LENGTH_PREFIX_LENGTH
        data = await self.reader.readexactly(max_len)
        (length,) = struct.unpack('!I', message_data)

        data = await self.reader.readexactly(length)
        message_id = MessageType(data[0])
        payload = memoryview[1:]

        return message_id, payload      
