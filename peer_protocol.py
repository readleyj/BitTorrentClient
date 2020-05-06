import asyncio
import config


class PeerConnection:
    def __init__(self, peer_queue: asyncio.Queue, client_id: int, info_hash: bytes) -> None:
        self.peer_id = peer_id
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

        self.task = asyncio.create_task(self.run())

    async def connect(self):
        pass

    async def send_handshake(self):
        pass

    async def receive_handshake(self):
        pass
