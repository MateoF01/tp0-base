import socket
import logging
import threading
from common.protocol import (
    recv_bets, send_ack, send_error, send_winners,
    recv_message_type, recv_agency_id
)
from common.utils import store_bets, load_bets, has_won
from .message_types import BET_BATCH, END


class Server:
    def __init__(self, port, listen_backlog, expected):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._expected_agencies = expected
        self._running = True

        # sincronización manual
        self._end_count = 0
        self._cond = threading.Condition()
        self._winners_by_agency = {}
        self._bets_lock = threading.Lock()


        self._threads = []

    def run(self):
        try:
            while self._running:
                try:
                    client_sock = self.__accept_new_connection()
                    t = threading.Thread(
                        target=self.__handle_client_connection,
                        args=(client_sock,)
                    )
                    t.start()
                    self._threads.append(t)
                except OSError:
                    if not self._running:
                        break
                    raise
        finally:
            for t in self._threads:
                t.join()

    def close(self):
        logging.info("action: shutdown | result: in_progress | resource: server")
        self._running = False
        self._server_socket.close()
        logging.info("action: shutdown | result: success | resource: socket")

    def __handle_client_connection(self, client_sock):
        try:
            agency_id = None
            while True:
                msg_type = recv_message_type(client_sock)
                if msg_type is None:
                    break

                if msg_type == BET_BATCH:
                    bets = recv_bets(client_sock)
                    if not bets:
                        break
                    agency_id = bets[0].agency
                    try:
                        #Seccion critica GUARDA BETS
                        with self._bets_lock:
                            store_bets(bets)

                        logging.info(
                            f"action: apuesta_recibida | result: success | cantidad: {len(bets)} | agency: {agency_id}"
                        )
                        send_ack(client_sock, len(bets))
                    except Exception as e:
                        logging.error(
                            f"action: apuesta_recibida | result: fail | cantidad: {len(bets)} | error: {e}"
                        )
                        send_error(client_sock, len(bets))

                elif msg_type == END:
                    agency_id = recv_agency_id(client_sock)
                    logging.info(f"action: end | result: success | agency: {agency_id}")

                    #El condition es muy bueno
                    #Cuando un hilo llega a esta seccion toma el lock interno del condition
                    #En ese momento puede sumar al contador y nadie mas podra entrar a la SC
                    #Como ve que la condicion no se cumple se pone en estado wait y libera el lock
                    #Y asi hasta que eventualmente llega a cumplirse la condicion
                    #Cuando un hilo entra a la seccion y la condicion se cumple el realizará
                    #el computo y notificará a todos de que ya pueden avanzar a enviar la respuesta

                    with self._cond:
                        self._end_count += 1
                        
                        if self._end_count == self._expected_agencies:
                            self._compute_winners()
                            self._cond.notify_all()  # despertar a todos
                        else:
                            self._cond.wait()

                    winners = self._winners_by_agency.get(int(agency_id), [])
                    send_winners(client_sock, winners)
                    logging.info(
                        f"action: send_winners | result: success | agency: {agency_id} | cantidad: {len(winners)}"
                    )
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
                winners_by_agency.setdefault(int(bet.agency), []).append(bet.document)
        self._winners_by_agency = winners_by_agency
        logging.info(f"action: sorteo | result: success | winners={self._winners_by_agency}")
