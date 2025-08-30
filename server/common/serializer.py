DELIM = "|"

def serialize_bet(bet):
    payload = DELIM.join([
        bet.documento,
        bet.nombre,
        bet.apellido,
        bet.nacimiento,
        bet.numero
    ])
    return payload.encode("utf-8")

def deserialize_bet(data: bytes):
    parts = data.decode("utf-8").split(DELIM)
    if len(parts) != 5:
        raise ValueError("Invalid payload")
    from .bet import Bet
    return Bet(*parts)
