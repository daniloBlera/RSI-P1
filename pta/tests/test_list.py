# -*- coding: utf-8 -*-
import socket
import unittest


class TestListRequests(unittest.TestCase):
    hostname = '127.0.0.1'
    port = 12000
    client_socket = None

    valid_user = 'user1'
    arquivos = 'arquivo2,arquivo1'

    cump_request = '{0} CUMP {1}'
    list_request = '{0} LIST'
    term_request = '{0} TERM'

    list_ok_response = '{0} ARQS {1} :END:'
    list_nok_response = '{0} NOK'

    ok_response = '{0} OK'
    nok_response = '{0} NOK'

    def setUp(self):
        self.client_socket = socket.socket(family=socket.AF_INET,
                                           type=socket.SOCK_STREAM)

        self.client_socket.connect((self.hostname, self.port))

    def tearDown(self):
        if self.client_socket is not None:
            self.client_socket.close()

    def test_LIST_without_previous_CUMP_request(self):
        seq_num = 1
        message = self.list_request.format(seq_num)

        self.client_socket.send(str.encode(message))
        response, address = self.client_socket.recvfrom(2048)

        expected = self.list_nok_response.format(seq_num)
        self.assertEqual(response.decode('utf-8'), expected)

    def test_LIST_with_previous_CUMP_request(self):
        seq_num = 1
        """Executando CUMP"""
        cump_message = self.cump_request.format(seq_num, self.valid_user)

        self.client_socket.sendall(str.encode(cump_message))
        cump_response, address = self.client_socket.recvfrom(2048)

        expected_cump_response = self.ok_response.format(seq_num)
        self.assertEqual(cump_response.decode('utf-8'), expected_cump_response)

        """Executando LIST"""
        seq_num += 1
        list_message = self.list_request.format(seq_num)

        self.client_socket.sendall(str.encode(list_message))
        list_response, address = self.client_socket.recvfrom(2048)

        expected_list_response = self.list_ok_response.format(seq_num,
                                                              self.arquivos)

        self.assertEqual(list_response.decode('utf-8'), expected_list_response)
