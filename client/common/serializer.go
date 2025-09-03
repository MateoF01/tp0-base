package common

import (
	"strconv"
	"strings"
)

const AckPartsNumber = 2

func SerializeBet(b Bet) []byte {
	payload := b.Agency + "|" +
		b.FirstName + "|" +
		b.LastName + "|" +
		b.Document + "|" +
		b.Birthdate + "|" +
		b.Number
	return []byte(payload)
}

func IntToBigEndianBytes(n uint32) []byte {
	return []byte{
		byte(n >> 24),
		byte(n >> 16),
		byte(n >> 8),
		byte(n),
	}
}

func BigEndianBytesToInt(b []byte) uint32 {
	return uint32(b[0])<<24 | uint32(b[1])<<16 | uint32(b[2])<<8 | uint32(b[3])
}

// DeserializeAck parsea un ACK tipo "OK|5" o "ERR|5"
func DeserializeAck(data []byte) (isOk bool, count int, err error) {
	
    parts := strings.SplitN(string(data), "|", AckPartsNumber)
	
    if len(parts) != AckPartsNumber {
		return false, 0, nil // mensaje mal formado → devolvemos false sin error técnico
	}

	count, err = strconv.Atoi(parts[1])
	if err != nil {
		return false, 0, err
	}

	switch parts[0] {
	case "OK":
		return true, count, nil
	case "ERR":
		return false, count, nil
	default:
		return false, 0, nil
	}
}
