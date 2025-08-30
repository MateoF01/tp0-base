import struct
from common.utils import Bet

DELIM = "|"

def serialize_bet(bet: Bet):
    payload = DELIM.join([
        str(bet.agency),
        bet.first_name,
        bet.last_name,
        bet.document,
        str(bet.birthdate),
        str(bet.number),
    ])
    data = payload.encode("utf-8")
    length = struct.pack(">I", len(data))
    return length + data

def deserialize_bet(data: bytes):
    parts = data.decode("utf-8").split(DELIM)
    if len(parts) != 6:
        raise ValueError("Invalid payload")
    return Bet(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])