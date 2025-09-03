package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
)

// LoadBetsBatch lee hasta batchSize apuestas desde el CSV
func LoadBetsBatch(reader *csv.Reader, agency string, batchSize int) ([]Bet, error) {
	var bets []Bet

	for len(bets) < batchSize {
		record, err := reader.Read()
		if err == io.EOF {
			break // fin del archivo
		}
		if err != nil {
			return nil, fmt.Errorf("failed to read dataset: %w", err)
		}

		if len(record) < 5 {
			return nil, fmt.Errorf("invalid record: %v", record)
		}

		bet := Bet{
			Agency:    agency,
			FirstName: record[0],
			LastName:  record[1],
			Document:  record[2],
			Birthdate: record[3],
			Number:    record[4],
		}
		bets = append(bets, bet)
	}

	return bets, nil
}
