package common

import (
    "bytes"
    "encoding/binary"
    "fmt"
    "io"
    "net"
    "strings"
)



func SendMessage(conn net.Conn, msgType byte, payload []byte) error {
    header := make([]byte, 5)
    header[0] = msgType
    binary.BigEndian.PutUint32(header[1:], uint32(len(payload)))
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

func SendHello(conn net.Conn, agencyID int) error {
    payload := []byte(fmt.Sprintf("%d", agencyID))
    return SendMessage(conn, MsgHello, payload)
}



func SendBets(conn net.Conn, bets []Bet) error {
    buf := new(bytes.Buffer)

    // cantidad de apuestas
    if err := binary.Write(buf, binary.BigEndian, uint32(len(bets))); err != nil {
        return err
    }

    // cada apuesta
    for _, b := range bets {
        data := SerializeBet(b)
        if err := binary.Write(buf, binary.BigEndian, uint32(len(data))); err != nil {
            return err
        }
        if _, err := buf.Write(data); err != nil {
            return err
        }
    }

    return SendMessage(conn, MsgBetBatch, buf.Bytes())
}

func SendEnd(conn net.Conn, agencyID int) error {
    payload := []byte(fmt.Sprintf("%d", agencyID))
    return SendMessage(conn, MsgFin, payload)
}

func SendGetWinners(conn net.Conn, agencyID int) error {
    payload := []byte(fmt.Sprintf("%d", agencyID))
    return SendMessage(conn, MsgGetWinners, payload)
}




func ReceiveMessage(conn net.Conn) (byte, []byte, error) {
	header := make([]byte, 5)
	if _, err := io.ReadFull(conn, header); err != nil {
		return 0, nil, err
	}
	msgType := header[0]
	length := binary.BigEndian.Uint32(header[1:5])

	payload := make([]byte, length)
	if _, err := io.ReadFull(conn, payload); err != nil {
		return 0, nil, err
	}
	return msgType, payload, nil
}

func ReceiveWinners(conn net.Conn) ([]string, error) {
	msgType, payload, err := ReceiveMessage(conn)
	if err != nil {
		return nil, err
	}
	if msgType != MsgWinners {
		return nil, fmt.Errorf("unexpected msg type: %d", msgType)
	}
	if len(payload) == 0 {
		return []string{}, nil
	}
	// payload es "dni1,dni2,dni3"
	list := strings.Split(string(payload), ",")
	// si el server manda vacío → string="" → []string{""}, filtramos
	if len(list) == 1 && list[0] == "" {
		return []string{}, nil
	}
	return list, nil
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