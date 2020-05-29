# Client Info
PEER_NAME = 'ET'
VERSION_NUM = '0001'
PORT_NUM = 6889

# Connection Parameters
PIECE_LENGTH = 20
COMPACT_PEER_SIZE = 6
DEFAULT_MIN_INTERVAL = 90
NUM_CONNECTIONS = 20
READ_TIMEOUT = 5

# Protocol Info
pstrlen = 19
pstr = b'BitTorrent protocol'
reserved_bytes = b'\0' * 8
HANDSHAKE_LENGTH = 68
LENGTH_PREFIX_SIZE = 4
