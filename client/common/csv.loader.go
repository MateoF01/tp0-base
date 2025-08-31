package common

import (
    "encoding/csv"
    "fmt"
    "io"
    "os"
)

func LoadBetsFromCSV(path string, agency string) ([]Bet, error) {
    file, err := os.Open(path)
    if err != nil {
        return nil, fmt.Errorf("failed to open dataset: %w", err)
    }
    defer file.Close()

    reader := csv.NewReader(file)
    var bets []Bet

    for {
        record, err := reader.Read()
        if err == io.EOF {
            break
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
