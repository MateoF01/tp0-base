from common.utils import Bet

DELIM = "|"
PARTS_NUMBER = 6

def deserialize_bet(data: bytes) -> Bet:

    parts = data.decode("utf-8").split(DELIM)
    if len(parts) != PARTS_NUMBER:
        raise ValueError(f"Invalid payload, expected 6 fields: {data}")

    return Bet(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])

def serialize_ack() -> bytes:
    return b"ACK"

def int_to_big_endian_bytes(n: int) -> bytes:
    return bytes([
        (n >> 24) & 0xFF,
        (n >> 16) & 0xFF,
        (n >> 8) & 0xFF,
        n & 0xFF
    ])

def big_endian_bytes_to_int(b: bytes) -> int:
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
