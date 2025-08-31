package common

import (
	"net"
	"time"
	"github.com/op/go-logging"
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {


	// Cargo apuestas desde CSV
	bets, err := LoadBetsFromCSV(c.config.DatasetPath, c.config.ID)
	if err != nil {
		log.Criticalf("action: load_bets | result: fail | error: %v", err)
		return
	}	
	
	//Voy dividiendo en batches del tamaño especificado en config
	for i := 0; i < len(bets); i += c.config.BatchMaxAmount {
		end := i + c.config.BatchMaxAmount
		if end > len(bets) {
			end = len(bets)
		}
		batch := bets[i:end]

		if err := c.createClientSocket(); err != nil {
			return
		}

		if err := SendBets(c.conn, batch); err != nil {
			log.Errorf("action: send_bets | result: fail | error: %v", err)
			c.conn.Close()
			return
		}

		isOk, betsCount, err := ReceiveAck(c.conn)
		c.conn.Close()

		if !isOk {
			log.Errorf("action: receive_ack | result: fail | error: %v", err)
			return
		}

		log.Infof("action: batch_enviado | result: success | cantidad: %d | ack: %s",
			betsCount, "ACK",
		)

		time.Sleep(c.config.LoopPeriod)
	}

	
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
