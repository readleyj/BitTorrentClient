import asyncio
import config
from models import Handshake


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
        print('Sending handshake')
        handshake = Handshake(self.info_hash, self.peer_id)
        self.writer.write(handshake.encode())
        await self.writer.drain()

    async def receive_handshake(self):
        print('Waiting for handshake')
        response = await self.reader.readexactly(config.HANDSHAKE_LENGTH)
        handshake = handshake.from_packed(response)

        if not handshake:
            raise ProtocolError('Could not receive and process handshake')

        if not handshake.info_hash == self.info_hash:
            raise ProtocolError('Received handshake with invalid info hash')

        if handshake.pstr != config.pstr or handshake.pstrlen != config.pstrlen:
            raise ProtocolError('Unknown protocol')

        self.remote_id = handshake.peer_id
        self.connected = True
        print('ID of remote peer is {}'.format(self.remote_id))