package common

import (
	"net"
	"time"
	"github.com/op/go-logging"
	"os"
    "encoding/csv"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	DatasetPath    string
	BatchMaxAmount int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// Close()  
func (c *Client) Close() {
    if c.conn != nil {
        c.conn.Close()
    }
}
// StartClientLoop Send messages to the server until all bets are sent
func (c *Client) StartClientLoop() {
	// Abrir archivo CSV
	file, err := os.Open(c.config.DatasetPath)
	if err != nil {
		log.Criticalf("action: open_dataset | result: fail | error: %v", err)
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Crear socket una sola vez
	if err := c.createClientSocket(); err != nil {
		return
	}
	defer c.conn.Close()

	for {
		// Leer siguiente batch
		batch, err := LoadBetsBatch(reader, c.config.ID, c.config.BatchMaxAmount)
		if err != nil {
			log.Errorf("action: load_bets | result: fail | error: %v", err)
			return
		}
		if len(batch) == 0 {
			break // no hay más apuestas → fin
		}

		// Enviar batch
		if err := SendBets(c.conn, batch); err != nil {
			log.Errorf("action: send_bets | result: fail | error: %v", err)
			return
		}

		// Esperar ACK
		isOk, betsCount, err := ReceiveAck(c.conn)
		if err != nil || !isOk {
			log.Errorf("action: receive_ack | result: fail | error: %v", err)
			return
		}

		log.Infof("action: batch_enviado | result: success | cantidad: %d | ack: ACK",
			betsCount,
		)

		time.Sleep(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
