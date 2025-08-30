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

    if err := binary.Write(conn, binary.BigEndian, length); err != nil {
        return err
    }
    _, err := conn.Write(data)
    return err
}

// Recibe un Bet con protocolo length-prefixed
func ReceiveBet(conn net.Conn) (Bet, error) {
    var length uint32
    if err := binary.Read(conn, binary.BigEndian, &length); err != nil {
        return Bet{}, err
    }

    buf := make([]byte, length)
    if _, err := io.ReadFull(conn, buf); err != nil {
        return Bet{}, err
    }

    return DeserializeBet(buf)
}

func SendAck(conn net.Conn, bet Bet) error {
    msg := fmt.Sprintf("ACK|%s|%s", bet.Document, bet.Number)
    data := []byte(msg)
    length := uint32(len(data))

    if err := binary.Write(conn, binary.BigEndian, length); err != nil {
        return err
    }
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
