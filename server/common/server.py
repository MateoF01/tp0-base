import socket
import logging
import threading
from common.protocol import (
    recv_bets, send_ack, send_error, send_winners,
    recv_message_type, recv_payload, recv_agency_id
)
from common.utils import store_bets, load_bets, has_won
from .message_types import BET_BATCH, END, WINNERS


class Server:
    def __init__(self, port, listen_backlog, expected):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._expected_agencies = expected
        self._running = True

        # sincronización
        self.barrier = threading.Barrier(expected)
        self._winners_by_agency = {}
        self._compute_lock = threading.Lock()  # para no computar dos veces

    def run(self):
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                # un hilo por cliente
                t = threading.Thread(
                    target=self.__handle_client_connection,
                    args=(client_sock,),
                    daemon=True
                )
                t.start()
            except OSError:
                if not self._running:
                    break
                raise

    def close(self):
        logging.info("action: shutdown | result: in_progress | resource: server")
        self._running = False
        self._server_socket.close()
        logging.info("action: shutdown | result: success | resource: socket")

    def __handle_client_connection(self, client_sock):
        try:
            while True:
                msg_type = recv_message_type(client_sock)
                if msg_type is None:
                    break

                if msg_type == BET_BATCH:
                    payload = recv_payload(client_sock)
                    agency_id, bets = recv_bets(payload)
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
                    payload = recv_payload(client_sock)
                    agency_id = recv_agency_id(payload)
                    logging.info(f"action: end | result: success | agency: {agency_id}")

                    # sincronizamos con la barrera
                    self.barrier.wait()

                    # un solo hilo hace el cómputo
                    with self._compute_lock:
                        if not self._winners_by_agency:
                            self._compute_winners()

                    # devolvemos los ganadores de esta agencia
                    winners = self._winners_by_agency.get(agency_id, [])
                    send_winners(client_sock, winners, WINNERS)
                    logging.info(f"action: winners_sent | result: success | agency: {agency_id}")
                    break

        except Exception as e:
            logging.error(f"action: handle_client | result: fail | error: {e}")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def __accept_new_connection(self):
        logging.info("action: accept_connections | result: in_progress")
        c, addr = self._server_socket.accept()
        logging.info(f"action: accept_connections | result: success | ip: {addr[0]}")
        return c

    def _compute_winners(self):
        winners_by_agency = {}
        for bet in load_bets():
            if has_won(bet):
                winners_by_agency.setdefault(bet.agency, []).append(bet.document)
        self._winners_by_agency = winners_by_agency
        logging.info(f"action: sorteo | result: success | winners_by_agency: {winners_by_agency}")
