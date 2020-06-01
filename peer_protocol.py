import asyncio
from enum import Enum

import config
from models import Handshake
from util import dispatch_on_value


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

        while True:
            message = self.receive_handshake()

            if message is None:
                continue

            message_id, payload = message
            self.handle_message(message_id, payload)

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
        max_len = config.LENGTH_PREFIX_SIZE
        data = await self.reader.readexactly(max_len)
        (length,) = struct.unpack('!I', message_data)

        # keep-alive
        if length == 0:
            return None

        data = await self.reader.readexactly(length)
        message_id = MessageType(data[0])
        payload = memoryview[1:]

        return message_id, payload   

    @dispatch_on_value
    def handle_message(message_id, payload):
        # This corresponds to an invalid message id. Raise exception here
        pass

    @handle_message.register(MessageType.CHOKE)
    def _(message_id, payload):
        self.peer_choking = True

    @handle_message.register(MessageType.UNCHOKE)
    def _(message_id, payload):
        self.peer_choking = False

    @handle_message.register(MessageType.INTERESTED)
    def _(message_id, payload):
        self.peer_interested = True

    @handle_message.register(MessageType.NOT_INTERESTED)
    def _(message_id, payload):
        self.peer_interested = False

    @handle_message.register(MessageType.HAVE)
    def _(message_id, payload):
        pass

    @handle_message.register(MessageType.BITFIELD)
    def _(message_id, payload):
        pass

    @handle_message.register(MessageType.REQUEST)
    def _(message_id, payload):
        pass
    
    @handle_message.register(MessageType.PIECE)
    def _(message_id, payload):
        pass

    @handle_message.register(MessageType.CANCEL)
    def _(message_id, payload):
        pass

    @handle_message.register(MessageType.PORT)
    def _(message_id, payload):
        pass
