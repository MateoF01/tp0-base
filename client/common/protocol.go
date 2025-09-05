package common

import (
	"net"
)

const (
	MSG_TYPE_BYTES = 1
	MSG_LEN_BYTES  = 4
)

// WriteFull asegura que se escriban todos los bytes o devuelva error
func WriteFull(conn net.Conn, data []byte) error {
	total := 0
	for total < len(data) {
		n, err := conn.Write(data[total:])
		if err != nil {
			return err
		}
		total += n
	}
	return nil
}

// ReadFullN lee exactamente n bytes o devuelve error
func ReadFullN(conn net.Conn, n int) ([]byte, error) {
	buf := make([]byte, n)
	total := 0
	for total < n {
		read, err := conn.Read(buf[total:])
		if err != nil {
			return nil, err
		}
		if read == 0 {
			return nil, &errorString{"unexpected message type"}
		}
		total += read
	}
	return buf, nil
}

// errorString es un tipo simple que implementa error
type errorString struct{ s string }
func (e *errorString) Error() string { return e.s }

func SendMessage(conn net.Conn, msgType byte, payload []byte) error {
	header := []byte{msgType}
	header = append(header, IntToBigEndianBytes(uint32(len(payload)))...)

	if err := WriteFull(conn, header); err != nil {
		return err
	}

	if len(payload) > 0 {
		if err := WriteFull(conn, payload); err != nil {
			return err
		}
	}
	return nil
}

func SendBets(conn net.Conn, bets []Bet) error {
	var msg []byte

	msg = append(msg, MsgBetBatch)
	msg = append(msg, IntToBigEndianBytes(uint32(len(bets)))...)

	for _, b := range bets {
		data := SerializeBet(b)
		msg = append(msg, IntToBigEndianBytes(uint32(len(data)))...)
		msg = append(msg, data...)
	}

	return WriteFull(conn, msg)
}

func SendEnd(conn net.Conn, agencyID string) error {
	return SendMessage(conn, MsgEnd, []byte(agencyID))
}

func SendGetWinners(conn net.Conn, agencyID string) error {
	return SendMessage(conn, MsgGetWinners, []byte(agencyID))
}

func ReceiveMessage(conn net.Conn) (byte, []byte, error) {
	header, err := ReadFullN(conn, MSG_TYPE_BYTES+MSG_LEN_BYTES)
	if err != nil {
		return 0, nil, err
	}
	msgType := header[0]
	length := int(BigEndianBytesToInt(header[MSG_TYPE_BYTES : MSG_TYPE_BYTES+MSG_LEN_BYTES]))

	payload, err := ReadFullN(conn, length)
	if err != nil {
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
	header, err := ReadFullN(conn, MSG_TYPE_BYTES)
	if err != nil {
		return nil, err
	}
	if header[0] != MsgWinners {
		return nil, nil
	}

	lenBuf, err := ReadFullN(conn, MSG_LEN_BYTES)
	if err != nil {
		return nil, err
	}
	n := int(BigEndianBytesToInt(lenBuf))

	winners := make([]string, 0, n)

	for i := 0; i < n; i++ {
		lenBuf, err = ReadFullN(conn, MSG_LEN_BYTES)
		if err != nil {
			return nil, err
		}
		l := int(BigEndianBytesToInt(lenBuf))

		data, err := ReadFullN(conn, l)
		if err != nil {
			return nil, err
		}
		winners = append(winners, string(data))
	}

	return winners, nil
}
