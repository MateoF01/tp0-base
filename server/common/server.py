from email import message
import socket
import logging
from common.protocol import recv_bets, send_ack, send_error,send_message, recv_message_type, recv_payload
from common.utils import store_bets, load_bets, has_won

from .message_types import HELLO, BET_BATCH, END, GET_WINNERS, ACK, ERR, WINNERS


class Server:
    def __init__(self, port, listen_backlog, expected):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._expected_agencies = expected

        self._running = True

        self._client_sockets = {}       # agency_id -> socket
        self._agencies_finished = {}    # agency_id -> bool
        self._pending_gets = {}         # agency_id -> socket (esperando WINNERS)
        self._winners_by_agency = {}    # agency_id -> [lista de wiiners]


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
        try:
            agency_id = None

            while True:
                try:
                    msg_type = recv_message_type(client_sock)
                    if msg_type is None:
                        break

                    if msg_type == HELLO:
                        payload = recv_payload(client_sock)
                        agency_id = int(payload.decode())
                        self._client_sockets[agency_id] = client_sock
                        self._agencies_finished[agency_id] = False
                        logging.info(
                            f"action: hello | result: success | agency: {agency_id}"
                        )

                    elif msg_type == BET_BATCH:
                        bets = recv_bets(client_sock, payload)
                        if not bets:
                            break
                        try:
                            store_bets(bets)
                            logging.info(
                                f"action: apuesta_recibida | result: success | cantidad: {len(bets)} | agency: {agency_id}"
                            )
                            send_ack(client_sock, f"OK|{len(bets)}")
                        except Exception as e:
                            logging.error(
                                f"action: apuesta_recibida | result: fail | cantidad: {len(bets)} | error: {e}"
                            )
                            send_error(client_sock, f"ERR|{len(bets)}")

                    elif msg_type == END:
                        if agency_id is None:
                            logging.error("END sin HELLO previo")
                            continue
                        self._agencies_finished[agency_id] = True
                        logging.info(
                            f"action: end | result: success | agency: {agency_id}"
                        )

                    elif msg_type == GET_WINNERS:
                        if agency_id is None:
                            logging.error("GET_WINNERS sin HELLO previo")
                            continue

                        # ¿ya todos terminaron?
                        if self.__all_finished():
                            # Más adelante: computar y responder ganadores
                            logging.info(
                                f"action: get_winners | result: ready | agency: {agency_id}"
                            )
                            self._compute_and_send_winners()

                            # Guardamos pendiente
                            self._pending_gets[agency_id] = client_sock
                            logging.info(
                                f"action: get_winners | result: waiting | agency: {agency_id}"
                            )

                except Exception as e:
                    logging.error(
                        f"action: handle_client | result: fail | error: {e}"
                    )
                    break
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

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

    def _compute_and_send_winners(self):
        # 1) Cargar todas las apuestas
        winners_by_agency = {}

        for bet in load_bets():
            if has_won(bet):
                winners_by_agency.setdefault(bet.agency, []).append(bet.document)

        # 2) Guardar resultado
        self._winners_by_agency = winners_by_agency

        # 3) Responder a todos los que estaban esperando
        for agency_id, sock in list(self._pending_gets.items()):
            winners = winners_by_agency.get(agency_id, [])
            payload = ",".join(winners).encode("utf-8")
            try:
                send_message(sock, WINNERS, payload)
                logging.info(
                    f"action: send_winners | result: success | agency: {agency_id} | cant_ganadores: {len(winners)}"
                )
            except Exception as e:
                logging.error(
                    f"action: send_winners | result: fail | agency: {agency_id} | error: {e}"
                )

        # 4) Vaciar pending_gets
        self._pending_gets.clear()

        logging.info("action: sorteo | result: success")

    def __all_finished(self) -> bool:
        """
        Devuelve True si tenemos exactamente _expected_agencies registradas
        y todas marcaron END.
        """
        if len(self._agencies_finished) < self._expected_agencies:
            return False
        return all(self._agencies_finished.values())
