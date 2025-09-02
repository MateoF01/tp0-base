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
