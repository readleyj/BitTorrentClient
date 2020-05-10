import asyncio

import config
from peer_protocol import PeerConnection
from announcer import Announcer, EventType
from models import Peer, Handshake
from torrent import TorrentInfo


class Client:
    def __init__(self, torrent: TorrentInfo) -> None:
        self.announcer = Announcer(torrent)
        self.peer_queue = asyncio.Queue()
        self.peer_connections = []
        self.executors = []

    async def start(self) -> None:
        self.peer_connections = [
            PeerConnection(self.peer_queue, self.announcer.peer_id, self.announcer.torrent.info_hash) for _ in range(config.NUM_CONNECTIONS)
        ]

        self.executors += [asyncio.ensure_future(conn.run()) for conn in self.peer_connections]

        while True:
            response = await self.announcer.announce(event=EventType.STARTED)

            if response:
                for peer in self.announcer.last_response.peers:
                    self.peer_queue.put_nowait(peer)

            if self.announcer.last_response.min_interval is not None:
                min_interval = self.announcer.last_response.min_interval
            else:
                min_interval = min(config.DEFAULT_MIN_INTERVAL, self.announcer.last_response.interval)

            await asyncio.sleep(min_interval)