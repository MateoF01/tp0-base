from common.utils import Bet

DELIM = "|"


BET_PARTS_NUMBER = 6

def int_to_big_endian_bytes(n: int) -> bytes:
    return bytes([
        (n >> 24) & 0xFF,
        (n >> 16) & 0xFF,
        (n >> 8) & 0xFF,
        n & 0xFF
    ])

def big_endian_bytes_to_int(b: bytes) -> int:
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]


# Serializers para payloads

def deserialize_bet(data: bytes) -> Bet:

    parts = data.decode("utf-8").split(DELIM)
    if len(parts) != BET_PARTS_NUMBER:
        raise ValueError(f"Invalid payload, expected 6 fields: {data}")

    return Bet(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])


def serialize_ack(count: int) -> bytes:
    return f"OK|{count}".encode("utf-8")

def serialize_error(count: int) -> bytes:
    return f"ERR|{count}".encode("utf-8")

def serialize_agency_id(agency_id: str) -> bytes:
    return agency_id.encode("utf-8")

def deserialize_agency_id(data: bytes) -> str:
    return data.decode("utf-8").strip()

def serialize_winners(winners: list[str]) -> bytes:
    payload = int_to_big_endian_bytes(len(winners))
    for w in winners:
        data = w.encode("utf-8")
        payload += int_to_big_endian_bytes(len(data)) + data
    return payload