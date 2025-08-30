import struct
import socket
from .serializer import serialize_bet, deserialize_bet

def send_bet(sock: socket.socket, bet):
    data = serialize_bet(bet)
    length = struct.pack(">I", len(data))
    sock.sendall(length + data)

def recv_bet(sock: socket.socket):
    raw_len = sock.recv(4)
    if not raw_len:
        return None
    msg_len = struct.unpack(">I", raw_len)[0]

    data = b""
    while len(data) < msg_len:
        packet = sock.recv(msg_len - len(data))
        if not packet:
            return None
        data += packet

    return deserialize_bet(data)

def send_ack(sock, bet):
    payload = f"ACK|{bet.document}|{bet.number}".encode("utf-8")
    length = struct.pack(">I", len(payload))
    sock.sendall(length + payload)

def recv_ack(sock):
    raw_len = sock.recv(4)
    if not raw_len:
        return None
    msg_len = struct.unpack(">I", raw_len)[0]

    data = b""
    while len(data) < msg_len:
        packet = sock.recv(msg_len - len(data))
        if not packet:
            return None
        data += packet

    return data.decode("utf-8")