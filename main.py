from bencodepy import encode, decode
import random
from torrent import TorrentInfo
from announcer import Announcer, EventType
from client import Client
import asyncio

new_torrent = TorrentInfo(torrent_url)
client = Client(new_torrent)

loop = asyncio.get_event_loop()
task = loop.create_task(client.start())
loop.run_until_complete(task)
