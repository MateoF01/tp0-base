package common

import (
    "fmt"
    "strings"
)

func SerializeBet(b Bet) []byte {
    payload := fmt.Sprintf("%s|%s|%s|%s|%s",
        b.Documento, b.Nombre, b.Apellido, b.Nacimiento, b.Numero)
    return []byte(payload)
}

func DeserializeBet(data []byte) (Bet, error) {
    parts := strings.Split(string(data), "|")
    if len(parts) != 5 {
        return Bet{}, fmt.Errorf("invalid payload: %s", string(data))
    }
    return Bet{
        Documento:  parts[0],
        Nombre:     parts[1],
        Apellido:   parts[2],
        Nacimiento: parts[3],
        Numero:     parts[4],
    }, nil
}
