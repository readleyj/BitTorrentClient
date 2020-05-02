import random
import logging
from urllib.parse import urlencode
from enum import Enum
from typing import Dict

import aiohttp
import bencodepy

import config
from torrent import TorrentInfo


class EventType(Enum):
    None = 0
    COMPLETED = 1
    STARTED = 2
    STOPPED = 3

# To Do
# 1. Currently the announcer only supports HTTP.
# Make announcer independent of protocol.
# Could create base tracker and
# subclass UDP and HTTP trackers from base
# 2. Cast response to OrderedDict and pass to functions to parse.
# Not sure if a separate response class is necessary

# I will probably have to pass a DownloadInfo into this.
# Hardcoding download values at 0 for now


class Response:
    def __init__(self, response) -> None:
        self.response = response

    @property
    def failure(self) -> bool:
        failure_reason = self.response.get(b'failure reason', '').decode()

        return failure_reason if failure_reason else None

    @property
    def interval(self) -> int:
        return self.response.get(b'interval', 0)

    @property
    def complete(self) -> int:
        return self.response.get(b'complete', 0)

    @property
    def incomplete(self) -> int:
        return self.response.get(b'incomplete', 0)

    @property
    def peers(self):
        peers = self.response[b'peers']

        peers = [peers[i: i + 6] for i in range(0, len(peers), 6)]
        return [Peer.from_compact(p) for p in peers]


class Announcer:
    def __init__(self, torrent: TorrentInfo) -> None:
        self.torrent = torrent
        self.peer_id = None
        self.http_client = aiohttp.ClientSession()

    async def announce(self, event: EventType) -> bool:
        req_params = self._get_request_params()

        if event.STARTED:
            req_params['event'] = 'started'

        connect_url = self.torrent.announce_url + '?' + urlencode(req_params)

        async with self.http_client.get(connect_url) as conn:
            if not response.status == 200:
                raise ConnectionError('Unable to connect to tracker')

            response = await conn.read()

        response = bencode.decode(response)

        if response:
            self.last_response = Response(response)
            return True

        return False
