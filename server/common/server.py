import socket
import logging
from common.protocol import recv_bets, send_ack, send_error
from common.utils import store_bets



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
            bets = recv_bets(client_sock)
            if not bets:
                logging.error("action: apuesta_recibida | result: fail | cantidad: 0 | error: empty_batch")
                send_error(client_sock, "ERR|0")
                return

            try:
                store_bets(bets)  # guarda todas las apuestas
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                send_ack(client_sock, f"OK|{len(bets)}")
            except Exception as e:
                logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)} | error: {e}")
                send_error(client_sock, f"ERR|{len(bets)}")

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
