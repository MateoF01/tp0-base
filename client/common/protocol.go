package common

import (
    "bytes"
    "encoding/binary"
    "fmt"
    "io"
    "net"
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
    // === 1) Leer header: tipo y longitud ===
    header := make([]byte, 5) // 1 byte tipo + 4 bytes length
    if _, err := io.ReadFull(conn, header); err != nil {
        return nil, fmt.Errorf("failed to read header: %w", err)
    }

    msgType := header[0]
    if msgType != MsgWinners { // tu constante WINNERS
        return nil, fmt.Errorf("unexpected msg type: %d", msgType)
    }

    length := int(binary.BigEndian.Uint32(header[1:5]))

    // === 2) Leer payload completo ===
    payload := make([]byte, length)
    if _, err := io.ReadFull(conn, payload); err != nil {
        return nil, fmt.Errorf("failed to read payload: %w", err)
    }

    // === 3) Parsear payload ===
    if len(payload) < 4 {
        return nil, fmt.Errorf("payload too short")
    }

    n := int(binary.BigEndian.Uint32(payload[0:4]))
    winners := make([]string, 0, n)

    offset := 4
    for i := 0; i < n; i++ {
        if offset+4 > len(payload) {
            return nil, fmt.Errorf("invalid payload (len missing)")
        }
        l := int(binary.BigEndian.Uint32(payload[offset : offset+4]))
        offset += 4

        if offset+l > len(payload) {
            return nil, fmt.Errorf("invalid payload (string overflow)")
        }
        w := string(payload[offset : offset+l])
        offset += l

        winners = append(winners, w)
    }

    return winners, nil
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