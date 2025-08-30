import socket
import logging
from common.protocol import recv_bet, send_ack
from utils import store_bet



class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._running = True


    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # DONE: Modify this program to handle signal to graceful shutdown
        # the server
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as e:
                if not self._running:  # si ya estoy apagando, cortar sin loguear error
                    break
                raise

    def close(self):
        logging.info("action: shutdown | result: in_progress | resource: server")
        self._running = False
        self._server_socket.close()
        logging.info("action: shutdown | result: success | resource: socket")

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # Recibo la apuesta
            bet = recv_bet(client_sock)
            if not bet:
                logging.error("action: receive_bet | result: fail | error: empty payload")
                return

            addr = client_sock.getpeername()
            logging.info(f"action: receive_bet | result: success | ip: {addr[0]} | dni: {bet.documento} | numero: {bet.numero}")

            # Persisto la apuesta
            store_bet(bet.documento, bet.nombre, bet.apellido, bet.nacimiento, bet.numero)

            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.documento} | numero: {bet.numero}")

            # Devuelvo ack
            send_ack(client_sock, bet)

        except Exception as e:
            logging.error(f"action: handle_client | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
