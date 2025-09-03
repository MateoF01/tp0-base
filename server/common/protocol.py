import socket
from .serializer import (
    deserialize_bet,
    serialize_ack,
    int_to_big_endian_bytes,
    big_endian_bytes_to_int
)

MSG_LEN_BYTES = 4   # cantidad de bytes reservados para la longitud


def recv_bet(sock: socket.socket):

    raw_len = sock.recv(MSG_LEN_BYTES)
    if not raw_len:
        return None

    msg_len = big_endian_bytes_to_int(raw_len)

    # Acumulo hasta leer todo el mensaje
    data = b""
    while len(data) < msg_len:
        packet = sock.recv(msg_len - len(data))
        if not packet:
            return None
        data += packet

    return deserialize_bet(data)

def send_ack(sock: socket.socket):
    payload = serialize_ack()
    length = int_to_big_endian_bytes(len(payload))
    sock.sendall(length + payload)
