import socket
from .serializer import (
    deserialize_bet,
    serialize_ack,
    serialize_error,
    int_to_big_endian_bytes,
    big_endian_bytes_to_int,
)

MSG_LEN_BYTES = 4

def recv_bets(sock: socket.socket):
    # Leo cantidad de apuestas (N)
    raw_n = sock.recv(MSG_LEN_BYTES)
    if not raw_n:
        return []
    n = big_endian_bytes_to_int(raw_n)

    bets = []
    for _ in range(n):
        # Leo longitud del payload
        raw_len = sock.recv(MSG_LEN_BYTES)
        if not raw_len:
            return []
        length = big_endian_bytes_to_int(raw_len)

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

def send_ack(sock: socket.socket, count: int):
    payload = serialize_ack(count)
    length = int_to_big_endian_bytes(len(payload))
    sock.sendall(length + payload)

def send_error(sock: socket.socket, count: int):
    payload = serialize_error(count)
    length = int_to_big_endian_bytes(len(payload))
    sock.sendall(length + payload)
