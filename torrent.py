from hashlib import sha1
from collections import namedtuple
from typing import List

import bencodepy.encode as bencode
from bencodepy import decode_from_file

# To Do
# 1. Support announce-list extension
# 2. Support multi-file torrents
# 3. Maybe implement private field
# 4. Maybe add DownloadInfo class


class FileInfo:
    def __init__(self):
        pass


class TorrentInfo:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.files = []

        with open(self.file_path, 'rb') as file:
            self.meta_info = decode_from_file(self.file_path)
            self.info_hash = sha1(bencode(self.meta_info[b'info'])).digest()

    # Optimize this. No need to compute on fly after it's computed once
    @property
    def pieces(self) -> List[bytes]:
        data = self.meta_info[b'info'][b'pieces']
        pieces = [data[offset: offset + config.PIECE_LENGTH]
                  for offset in range(0, len(data), config.PIECE_LENGTH)]
        return pieces

    @property
    def announce_url(self) -> str:
        return self.meta_info[b'announce'].decode('utf-8')

    @property
    def piece_length(self) -> int:
        return self.meta_info[b'info'][b'piece length']

    @property
    def is_single_file(self) -> bool:
        return b'files' not in self.meta_info[b'info']

    @property
    def creation_date(self) -> int:
        return self.meta_info[b'creation date']

    @property
    def file_length(self) -> int:
        return self.meta_info[b'info'][b'length']

    @property
    def file_name(self) -> str:
        return self.meta_info[b'info'][b'name'].decode('utf-8')

    def _get_files(self):
        # This should be in FileInfo
        pass
