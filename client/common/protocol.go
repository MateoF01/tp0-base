package common

import (
    "io"
    "net"
)


func SendMessage(conn net.Conn, msgType byte, payload []byte) error {
	header := []byte{msgType}
	header = append(header, IntToBigEndianBytes(uint32(len(payload)))...)
	if _, err := conn.Write(header); err != nil {
		return err
	}
	if len(payload) > 0 {
		if _, err := conn.Write(payload); err != nil {
			return err
		}
	}
	return nil
}

func SendBets(conn net.Conn, bets []Bet) error {
	var msg []byte

	// tipo de mensaje
	msg = append(msg, MsgBetBatch)

	// cantidad de apuestas
	msg = append(msg, IntToBigEndianBytes(uint32(len(bets)))...)

	// cada apuesta
	for _, b := range bets {
		data := SerializeBet(b)
		msg = append(msg, IntToBigEndianBytes(uint32(len(data)))...)
		msg = append(msg, data...)
	}

	// enviar todo junto
	_, err := conn.Write(msg)
	return err
}


func SendEnd(conn net.Conn, agencyID string) error {
	return SendMessage(conn, MsgEnd, []byte(agencyID))
}

func SendGetWinners(conn net.Conn, agencyID string) error {
	return SendMessage(conn, MsgGetWinners, []byte(agencyID))
}

func ReceiveMessage(conn net.Conn) (byte, []byte, error) {
	header := make([]byte, 5)
	if _, err := io.ReadFull(conn, header); err != nil {
		return 0, nil, err
	}
	msgType := header[0]
	length := BigEndianBytesToInt(header[1:5])

	payload := make([]byte, length)
	if _, err := io.ReadFull(conn, payload); err != nil {
		return 0, nil, err
	}
	return msgType, payload, nil
}

func ReceiveAck(conn net.Conn) (bool, int, error) {
	msgType, payload, err := ReceiveMessage(conn)
	if err != nil {
		return false, 0, err
	}
	if msgType != MsgAck && msgType != MsgErr {
		return false, 0, nil
	}
	return DeserializeAck(payload)
}

func ReceiveWinners(conn net.Conn) ([]string, error) {
	// leer tipo de mensaje
	header := make([]byte, 1)
	if _, err := io.ReadFull(conn, header); err != nil {
		return nil, err
	}
	if header[0] != MsgWinners {
		return nil, nil // tipo inesperado
	}

	// cantidad de ganadores
	lenBuf := make([]byte, 4)
	if _, err := io.ReadFull(conn, lenBuf); err != nil {
		return nil, err
	}
	n := int(BigEndianBytesToInt(lenBuf))

	winners := make([]string, 0, n)

	// cada ganador
	for i := 0; i < n; i++ {
		// longitud del string
		if _, err := io.ReadFull(conn, lenBuf); err != nil {
			return nil, err
		}
		l := int(BigEndianBytesToInt(lenBuf))

		// leer string
		data := make([]byte, l)
		if _, err := io.ReadFull(conn, data); err != nil {
			return nil, err
		}

		winners = append(winners, string(data))
	}

	return winners, nil
}
