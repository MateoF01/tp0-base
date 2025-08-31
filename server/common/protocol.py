import struct
import socket
from .serializer import deserialize_bet


def recv_bets(sock):
    # Leo cantidad de apuestas (N)
    raw_n = sock.recv(4)
    if not raw_n:
        return []
    n = struct.unpack(">I", raw_n)[0]

    bets = []
    for _ in range(n):
        # Leo longitud del payload
        raw_len = sock.recv(4)
        if not raw_len:
            return []
        length = struct.unpack(">I", raw_len)[0]

        # Leo payload completo
        data = b""
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return []
            data += packet

        bet = deserialize_bet(data)
        bets.append(bet)

    return bets


def send_ack(sock, msg: str):
    data = msg.encode("utf-8")
    length = struct.pack(">I", len(data))
    sock.sendall(length + data)

def send_error(sock, msg: str):
    data = msg.encode("utf-8")
    length = struct.pack(">I", len(data))
    sock.sendall(length + data)

