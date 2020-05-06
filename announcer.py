import random
import logging
from urllib.parse import urlencode
from enum import Enum
from typing import Dict
from collections import OrderedDict

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
    def __init__(self, response: OrderedDict) -> None:
        self.response = response
        self.parse_required_fields()
        self.parse_optional_fields()

    def parse_required_fields(self) -> None:
        self.failure_reason = self.response.get(b'failure reason', None)

        if self.failure_reason:
            raiseTrackerError(self.failure_reason.decode('utf-8'))

        self.interval = self.response[b'interval']
        self.min_interval = self.response.get(b'min interval', None)

        peers = self.response[b'peers']

        if isinstance(peers, bytes):
            size = config.COMPACT_PEER_SIZE
            peers = [peers[i: i + size] for i in range(0, len(peers), size)]
            self.peers = [Peer.from_compact(p) for p in peers]
        else:
            pass
            # Handle dict

    def parse_optional_fields(self) -> None:
        self.warning_message = self.response(b'warning message', None)

        if self.warning_message:
            logger.warning('Tracker returned warning {}',
                           self.response.warning_message.decode('utf-8'))

        self.tracker_id = self.response.get(b'tracker id', None)
        self.seed_count = self.response(b'complete', None)
        self.leech_count = self.response(b'incomplete', None)


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
