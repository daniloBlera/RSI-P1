# -*- coding: utf-8 -*-
import socket
import unittest


class TestTermRequests(unittest.TestCase):
    hostname = '127.0.0.1'
    port = 12000
    client_socket = None

    valid_user = 'user1'

    cump_request = '{0} CUMP {1}'
    term_request = '{0} TERM'

    ok_response = '{0} OK'
    nok_response = '{0} NOK'

    def setUp(self):
        self.client_socket = socket.socket(family=socket.AF_INET,
                                           type=socket.SOCK_STREAM)

        self.client_socket.connect((self.hostname, self.port))

    def tearDown(self):
        if self.client_socket is not None:
            self.client_socket.close()

    def test_response_without_previous_CUMP(self):
        seq_num = 1

        term_message = self.term_request.format(seq_num)
        self.client_socket.sendall(str.encode(term_message))
        term_response, address = self.client_socket.recvfrom(2048)

        expected = self.nok_response.format(seq_num)
        self.assertEqual(term_response.decode('utf-8'), expected)

    def test_response_with_previous_CUMP(self):
        seq_num = 1
        cump_message = self.cump_request.format(seq_num, self.valid_user)
        self.client_socket.sendall(str.encode(cump_message))
        cump_response, address = self.client_socket.recvfrom(2048)

        expected_cump_response = self.ok_response.format(seq_num)
        self.assertEqual(cump_response.decode("utf-8"), expected_cump_response)

        second_seq_num = seq_num + 1
        term_message = self.term_request.format(second_seq_num)
        self.client_socket.sendall(str.encode(term_message))
        term_response, address = self.client_socket.recvfrom(2048)

        expected_term_response = self.ok_response.format(second_seq_num)
        self.assertEqual(term_response.decode("utf-8"), expected_term_response)

    def test_server_closes_connection_on_TERM(self):
        seq_num = 99
        cump_request = self.cump_request.format(seq_num, self.valid_user)

        """Iniciando sessão com CUMP"""
        self.client_socket.sendall(str.encode(cump_request))
        cump_response, address = self.client_socket.recvfrom(2048)

        expected_cump_response = self.ok_response.format(seq_num)
        self.assertEqual(cump_response.decode("utf-8"), expected_cump_response)

        seq_num += 1
        term_request = self.term_request.format(seq_num)

        """Requisitando encerramento de sessão/socket de comunicação"""
        self.client_socket.sendall(str.encode(term_request))
        term_response, address = self.client_socket.recvfrom(2048)

        expected_term_response = self.ok_response.format(seq_num)
        self.assertEqual(term_response.decode("utf-8"), expected_term_response)

        seq_num += 1
        """Enviando novo CUMP em socket fechado"""
        new_cump_request = self.cump_request.format(seq_num, self.valid_user)

        """Enviando CUMP através de socket fechado no servidor"""
        self.client_socket.sendall(str.encode(new_cump_request))

        self.assertRaises(
            ConnectionResetError, self.client_socket.recvfrom, 2048)
