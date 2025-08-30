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

	//ej5
	Nombre    string
    Apellido  string
    Documento string
    Nacimiento string
    Numero    string
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
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		
		if err := c.createClientSocket(); err != nil {
			return
		}

		//Construyo la apuesta tomando los datos de config
		bet := Bet{
			Agency:    c.config.ID,
			FirstName: c.config.Nombre,
			LastName:  c.config.Apellido,
			Document:  c.config.Documento,
			Birthdate: c.config.Nacimiento,
			Number:    c.config.Numero,
		}

		// Enviar la apuesta
		err := SendBet(c.conn, bet)
		if err != nil {
			log.Errorf("action: send_bet | result: fail | dni: %s | error: %v",
				bet.Document, err,
			)
			c.conn.Close()
			return
		}

		// Esperar el ACK
		ack, err := ReceiveAck(c.conn)
		c.conn.Close() // cerramos la conexión después de recibir el ACK

		if err != nil {
			log.Errorf("action: receive_ack | result: fail | dni: %s | error: %v",
				bet.Document, err,
			)
			return
		}

		// Loguear el éxito
		log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %s | ack: %s",
			bet.Document, bet.Number, ack,
		)


		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
