import socket
from .serializer import (
    deserialize_bet,
    serialize_ack,
    serialize_error,
    serialize_agency_id,
    deserialize_agency_id,
    serialize_winners,
    int_to_big_endian_bytes,
    big_endian_bytes_to_int,
)
from .message_types import ACK, ERR, WINNERS


MSG_TYPE_BYTES = 1
MSG_LEN_BYTES = 4

def recv_message_type(sock: socket.socket) -> int:
    raw_type = sock.recv(MSG_TYPE_BYTES)
    if not raw_type:
        return None
    return raw_type[0]


def recv_payload(sock: socket.socket) -> bytes:
    # Leo longitud del payload
    raw_len = sock.recv(MSG_LEN_BYTES)
    if not raw_len:
        return None
    length = big_endian_bytes_to_int(raw_len)

    # Leo payload completo
    data = b""
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet

    return data


def recv_bets(sock: socket.socket):
    # cantidad de apuestas
    raw_n = sock.recv(MSG_LEN_BYTES)
    if not raw_n:
        return []
    n = big_endian_bytes_to_int(raw_n)

    bets = []
    for _ in range(n):
        data = recv_payload(sock)
        if not data:
            return []
        bet = deserialize_bet(data)
        bets.append(bet)

    return bets


def recv_agency_id(sock: socket.socket) -> str:
    data = recv_payload(sock)
    if not data:
        return None
    return deserialize_agency_id(data)

def send_message(sock: socket.socket, msg_type: int, payload: bytes):
    header = bytes([msg_type]) + int_to_big_endian_bytes(len(payload))
    sock.sendall(header + payload)

def send_ack(sock: socket.socket, count: int):
    payload = serialize_ack(count)
    send_message(sock, ACK, payload)   # ACK es una constante con el código de mensaje

def send_error(sock: socket.socket, count: int):
    payload = serialize_error(count)
    send_message(sock, ERR, payload)   # ERR es una constante con el código de mensaje

def send_winners(sock: socket.socket, winners: list[str]):
    # armo el mensaje completo
    msg = bytes([WINNERS])

    # cantidad de ganadores
    msg += int_to_big_endian_bytes(len(winners))

    # cada ganador
    for w in winners:
        data = w.encode("utf-8")
        msg += int_to_big_endian_bytes(len(data))
        msg += data

    sock.sendall(msg)
