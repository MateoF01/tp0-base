package common

import (
    "fmt"
    "strings"
)

func SerializeBet(b Bet) []byte {
    payload := fmt.Sprintf("%s|%s|%s|%s|%s|%s",
        b.Agency, b.FirstName, b.LastName, b.Document, b.Birthdate, b.Number)
    return []byte(payload)
}

func DeserializeBet(data []byte) (Bet, error) {
    parts := strings.Split(string(data), "|")
    if len(parts) != 6 {
        return Bet{}, fmt.Errorf("invalid payload: %s", string(data))
    }
    return Bet{
        Agency:    parts[0],
        FirstName: parts[1],
        LastName:  parts[2],
        Document:  parts[3],
        Birthdate: parts[4],
        Number:    parts[5],
    }, nil
}
