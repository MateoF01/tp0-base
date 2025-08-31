package common

import (
    "encoding/binary"
    "io"
    "net"
)


func SendBets(conn net.Conn, bets []Bet) error {
    // Escribir cantidad de apuestas
    if err := binary.Write(conn, binary.BigEndian, uint32(len(bets))); err != nil {
        return err
    }

    // Escribir cada apuesta
    for _, b := range bets {
        data := SerializeBet(b)
        if err := binary.Write(conn, binary.BigEndian, uint32(len(data))); err != nil {
            return err
        }
        if _, err := conn.Write(data); err != nil {
            return err
        }
    }
    return nil
}


func ReceiveAck(conn net.Conn) (bool, int, error) {
    var length uint32
    if err := binary.Read(conn, binary.BigEndian, &length); err != nil {
        return false, 0, err
    }

    data := make([]byte, length)
    if _, err := io.ReadFull(conn, data); err != nil {
        return false, 0, err
    }

    return DeserializeAck(data)
}