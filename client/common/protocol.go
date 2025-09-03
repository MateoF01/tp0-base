package common

import (
	"io"
	"net"
)

const MsgLenBytes = 4 // cantidad de bytes para la longitud en big endian

func SendBets(conn net.Conn, bets []Bet) error {
	// Escribo cantidad de apuestas (N)
	if _, err := conn.Write(IntToBigEndianBytes(uint32(len(bets)))); err != nil {
		return err
	}

	// Escribo cada apuesta
	for _, b := range bets {
		data := SerializeBet(b)

		// Primero longitud del payload
		if _, err := conn.Write(IntToBigEndianBytes(uint32(len(data)))); err != nil {
			return err
		}

		// Después el payload
		if _, err := conn.Write(data); err != nil {
			return err
		}
	}
	return nil
}

func ReceiveAck(conn net.Conn) (bool, int, error) {
	// Leo encabezado con longitud
	lenBytes := make([]byte, MsgLenBytes)
	if _, err := io.ReadFull(conn, lenBytes); err != nil {
		return false, 0, err
	}
	length := BigEndianBytesToInt(lenBytes)

	// Leo payload
	data := make([]byte, length)
	if _, err := io.ReadFull(conn, data); err != nil {
		return false, 0, err
	}

	return DeserializeAck(data)
}
