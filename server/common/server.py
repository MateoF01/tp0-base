import socket
import logging
from common.protocol import (
    recv_bets, send_ack, send_error, send_winners,
    recv_message_type, recv_payload, recv_agency_id
)
from common.utils import store_bets, load_bets, has_won
from .message_types import HELLO, BET_BATCH, END, WINNERS, GET_WINNERS


class Server:
    def __init__(self, port, listen_backlog, expected):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._expected_agencies = expected

        self._running = True

        self._agencies_finished = 0    # agency_id -> bool
        self._winners_by_agency = {}    # agency_id -> [dni ganadores]

    def run(self):
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as e:
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
                    self._agencies_finished += 1
                    payload = recv_payload(client_sock)
                    agency_id = recv_agency_id(payload)

                    logging.info(f"action: end | result: success | agency: {agency_id}")
                    break



                elif msg_type == GET_WINNERS:
                    payload = recv_payload(client_sock)
                    agency_id = recv_agency_id(payload)

                    logging.info(f"action: get_winners | result: in_progress | agency: {agency_id}")

                    if self._agencies_finished == self._expected_agencies:
                        if(len(self._winners_by_agency) == 0 ): #Si todavia no computamos, computamos
                            self._compute_winners()                        

                        send_winners(client_sock, self._winners_by_agency[agency_id], WINNERS)
                        logging.info(f"action: get_winners | result: sucecess | agency: {agency_id}")

                    break

        except Exception as e:
            logging.error(f"action: handle_client | result: fail | error: {e}")
        finally:
            # si por algún motivo salimos del loop antes
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

        logging.info(f"action: sorteo | result: success")
    

  