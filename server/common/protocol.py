import struct
from .serializer import deserialize_bet


def recv_message_type(sock) -> int:
    """
    Lee solo 1 byte con el tipo de mensaje.
    Devuelve un int (0-255).
    """
    raw_type = sock.recv(1)
    if not raw_type:
        return None
    return raw_type[0]  # convierte de bytes a int


def recv_payload(sock) -> bytes:
    """
    Lee un payload genérico: primero uint32 length, luego length bytes.
    """
    raw_len = sock.recv(4)
    if not raw_len:
        return b""
    length = struct.unpack(">I", raw_len)[0]

    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def recv_bets(sock) -> list:
    """
    Lee un payload de tipo BET_BATCH usando el formato actual:
      - uint32 N
      - N veces: [uint32 len + bet_payload]
    """
    raw_n = sock.recv(4)
    if not raw_n:
        return []
    n = struct.unpack(">I", raw_n)[0]

    bets = []
    for _ in range(n):
        raw_len = sock.recv(4)
        if not raw_len:
            return []
        length = struct.unpack(">I", raw_len)[0]

        data = b""
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return []
            data += packet

        bet = deserialize_bet(data)
        bets.append(bet)

    return bets


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
