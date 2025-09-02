from common.utils import Bet

DELIM = "|"

def deserialize_bet(data: bytes) -> Bet:

    parts = data.decode("utf-8").split(DELIM)
    if len(parts) != 6:
        raise ValueError(f"Invalid payload, expected 6 fields: {data}")

    return Bet(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
