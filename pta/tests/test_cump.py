# -*- coding: utf-8 -*-
import socket
import unittest


class TestCumpRequests(unittest.TestCase):
    hostname = '127.0.0.1'
    port = 12000
    client_socket = None

    request = '{0} CUMP {1}'
    response = '{0} {1}'

    ok_response = '{0} OK'
    nok_response = '{0} NOK'

    def setUp(self):
        self.client_socket = socket.socket(family=socket.AF_INET,
                                           type=socket.SOCK_STREAM)

        self.client_socket.connect((self.hostname, self.port))

    def tearDown(self):
        if self.client_socket is not None:
            self.client_socket.close()

    def test_CUMP_response_with_valid_user(self):
        user = 'user1'
        seq_num = 1

        message = self.request.format(seq_num, user)

        self.client_socket.send(str.encode(message))
        response, address = self.client_socket.recvfrom(2048)

        expected = self.response.format(seq_num, 'OK')
        self.assertEqual(response.decode('utf-8'), expected)

    def test_CUMP_response_with_invalid_user(self):
        user = 'this_user_doesnt_exists'
        seq_num = 1

        message = self.request.format(seq_num, user)

        self.client_socket.send(str.encode(message))
        response, address = self.client_socket.recvfrom(2048)

        expected = self.response.format(seq_num, 'NOK')
        self.assertEqual(response.decode('utf-8'), expected)

    def test_CUMP_request_and_response_SEQ_NUM_are_equal(self):
        user = 'some_invalid_username'
        seq_num = 1001
        message = self.request.format(seq_num, user)

        self.client_socket.send(str.encode(message))
        response, address = self.client_socket.recvfrom(2048)

        expected = self.response.format(seq_num, 'NOK')
        self.assertEqual(response.decode('utf-8'), expected)

    def test_CUMP_request_during_session_returns_NOK(self):
        user = 'user1'
        seq_num = 10
        message = self.request.format(seq_num, user)

        """Primeiro CUMP"""
        self.client_socket.sendall(str.encode(message))
        response, addres = self.client_socket.recvfrom(2048)

        expected = self.ok_response.format(seq_num)
        self.assertEqual(response.decode("utf-8"), expected)

        seq_num += 1
        message = self.request.format(seq_num, user)

        """Segundo CUMP, dentro de uma sessão"""
        self.client_socket.sendall(str.encode(message))
        response, addres = self.client_socket.recvfrom(2048)

        expected = self.nok_response.format(seq_num)
        self.assertEqual(response.decode("utf-8"), expected)
