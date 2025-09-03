package common

import (
	"io"
	"net"
)

const MsgLenBytes = 4 // cantidad de bytes reservados para la longitud

func SendBet(conn net.Conn, b Bet) error {
	data := SerializeBet(b)
	length := uint32(len(data))

	// serializo longitud en big endian
	lenBytes := IntToBigEndianBytes(length)

	if _, err := conn.Write(lenBytes); err != nil {
		return err
	}

	if _, err := conn.Write(data); err != nil {
		return err
	}

	return nil
}

func ReceiveAck(conn net.Conn) (string, error) {

    // recibo 4 bytes de longitud
	lenBytes := make([]byte, MsgLenBytes)
	if _, err := io.ReadFull(conn, lenBytes); err != nil {
		return "", err
	}
	length := BigEndianBytesToInt(lenBytes)

	// recibo payload
	buf := make([]byte, length)
	if _, err := io.ReadFull(conn, buf); err != nil {
		return "", err
	}

	return string(buf), nil
}
