import struct
from .serializer import deserialize_bet


def recv_message_type(sock) -> int:
    """
    Lee solo el byte de tipo de mensaje.
    """
    raw_type = sock.recv(1)
    if not raw_type:
        return None
    return raw_type[0]


def recv_payload(sock) -> bytes:
    raw_len = sock.recv(4)
    if not raw_len or len(raw_len) < 4:
        return b""
    length = struct.unpack(">I", raw_len)[0]

    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return b""
        data += chunk
    return data



def recv_bets(payload: bytes):
    """
    Decodifica un payload de tipo BET_BATCH.
    Formato:
      [uint32 N]
      N veces: [uint32 len][bet_payload]
    """
    if not payload:
        return []

    # cantidad de apuestas
    n = struct.unpack(">I", payload[:4])[0]
    offset = 4

    bets = []
    for _ in range(n):
        # longitud del bet
        length = struct.unpack(">I", payload[offset:offset+4])[0]
        offset += 4

        data = payload[offset:offset+length]
        offset += length

        bet = deserialize_bet(data)
        bets.append(bet)

    return bets[0].agency, bets


def send_message(sock, msg_type: int, payload: bytes):
    """
    Envia un mensaje con framing:
      [1 byte tipo][4 bytes length][payload]
    """
    header = struct.pack(">BI", msg_type, len(payload))
    sock.sendall(header + payload)


def send_ack(sock, msg: str):
    data = msg.encode("utf-8")
    length = struct.pack(">I", len(data))
    sock.sendall(length + data)


def send_error(sock, msg: str):
    data = msg.encode("utf-8")
    length = struct.pack(">I", len(data))
    sock.sendall(length + data)

def recv_agency_id(payload: bytes) -> int:

    if not payload:
        return None
    try:
        return int(payload.decode("utf-8").strip())
    except ValueError:
        return None

def send_winners(sock, winners: list[str], msg_type: int = 3):
    payload = struct.pack(">I", len(winners))  # cantidad N

    for w in winners:
        data = w.encode("utf-8")
        payload += struct.pack(">I", len(data)) + data

    send_message(sock, msg_type, payload)
