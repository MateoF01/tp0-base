package common

import (
    "encoding/binary"
    "io"
    "net"
	"fmt"
)

// Envía un Bet con protocolo length-prefixed
func SendBet(conn net.Conn, b Bet) error {
    data := SerializeBet(b)
    length := uint32(len(data))

    //indico tamanio
    if err := binary.Write(conn, binary.BigEndian, length); err != nil {
        return err
    }

    //envio payload
    _, err := conn.Write(data)
    return err
}

func ReceiveAck(conn net.Conn) (string, error) {
    var length uint32
    if err := binary.Read(conn, binary.BigEndian, &length); err != nil {
        return "", err
    }

    buf := make([]byte, length)
    if _, err := io.ReadFull(conn, buf); err != nil {
        return "", err
    }

    return string(buf), nil
}
