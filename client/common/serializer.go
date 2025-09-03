package common

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