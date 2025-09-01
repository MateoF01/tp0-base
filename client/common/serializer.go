package common

import (
    "fmt"
    "strings"
	"strconv"
)

func SerializeBet(b Bet) []byte {
    payload := fmt.Sprintf("%s|%s|%s|%s|%s|%s",
        strconv.Itoa(b.Agency),    // int -> string (otra vez)
        b.FirstName,               // string
        b.LastName,                // string
        b.Document,                // string
        b.Birthdate,               // string "YYYY-MM-DD"
        b.Number,    			   // string
    )
    return []byte(payload)
}

func DeserializeAck(data []byte) (isOk bool, count int, err error) {
    parts := strings.SplitN(string(data), "|", 2)
    if len(parts) != 2 {
        return false, 0, fmt.Errorf("invalid ack format: %s", string(data))
    }

    count, convErr := strconv.Atoi(parts[1])
    if convErr != nil {
        return false, 0, fmt.Errorf("invalid count in ack: %s", parts[1])
    }

    switch parts[0] {
    case "OK":
        return true, count, nil
    case "ERR":
        return false, count, nil
    default:
        return false, 0, fmt.Errorf("unknown ack status: %s", parts[0])
    }
}
