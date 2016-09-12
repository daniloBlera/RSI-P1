# -*- coding: utf-8 -*-
import os
import socket
import unittest


class TestPegaRequests(unittest.TestCase):
    hostname = '127.0.0.1'
    port = 12000
    client_socket = None

    valid_user = 'user1'

    current_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    file_dir = '{0}/arquivos/'.format(parent_dir)

    file1 = 'arquivo1'
    file2 = 'arquivo2'

    file_list = os.listdir(file_dir)
    files_arg = ','.join(file_list)

    cump_request = '{0} CUMP {1}'
    list_request = '{0} LIST'
    pega_request = '{0} PEGA {1}'
    term_request = '{0} TERM'

    ok_response = '{0} OK'
    nok_response = '{0} NOK'
    list_ok_response = '{0} ARQS {1} :END:'
    pega_ok_response = '{0} ARQ {1} :END:'

    def setUp(self):
        self.client_socket = socket.socket(family=socket.AF_INET,
                                           type=socket.SOCK_STREAM)

        self.client_socket.connect((self.hostname, self.port))

    def tearDown(self):
        if self.client_socket is not None:
            self.client_socket.close()

    def test_returns_nok_on_invalid_file(self):
        missing_file = 'this_is_some_non_existing_file'

        """CUMP Request"""
        seq_num = 1
        cump_request = self.cump_request.format(seq_num, self.valid_user)
        self.client_socket.sendall(str.encode(cump_request))
        cump_response, address = self.client_socket.recvfrom(2048)

        expected_cump_response = self.ok_response.format(seq_num)
        self.assertEqual(cump_response.decode("utf-8"), expected_cump_response)

        """PEGA Request"""
        seq_num += 1
        pega_request = self.pega_request.format(seq_num, missing_file)
        self.client_socket.sendall(str.encode(pega_request))
        response, address = self.client_socket.recvfrom(2048)

        expected = self.nok_response.format(seq_num)
        self.assertEqual(response.decode("utf-8"), expected)

    def test_transfer_file(self):
        src_file = 'arquivo2'
        dst_file = 'destiny_arquivo1'

        """CUMP Request"""
        seq_num = 1
        cump_request = self.cump_request.format(seq_num, self.valid_user)
        self.client_socket.sendall(str.encode(cump_request))
        cump_response, address = self.client_socket.recvfrom(2048)

        expected_cump_response = self.ok_response.format(seq_num)
        self.assertEqual(cump_response.decode("utf-8"), expected_cump_response)

        """LIST Request"""
        seq_num += 1
        list_request = self.list_request.format(seq_num)
        self.client_socket.sendall(str.encode(list_request))
        list_response, address = self.client_socket.recvfrom(2048)

        expected_list_response = self.list_ok_response.format(
            seq_num, self.files_arg)

        self.assertEqual(list_response.decode("utf-8"), expected_list_response)

        """PEGA Request"""
        seq_num += 1
        pega_request = self.pega_request.format(seq_num, src_file)
        self.client_socket.sendall(str.encode(pega_request))

        data1 = ""
        while 1:
            data, addr = self.client_socket.recvfrom(2048)
            data1 += data.decode('utf-8')
            if b"NOK" in data:
                break
            if b":END:" in data:
                break

        if ":END:" in data1:
            f = open(dst_file, "w")
            f.write(data1[6:].strip(" :END:"))
            f.close()

        recieved_file = open(dst_file, 'r')
        recieved_content = recieved_file.read()
        recieved_file.close()

        original_file = open(self.file_dir + src_file, 'r')
        original_content = original_file.read()
        original_file.close()

        self.assertEqual(recieved_content, original_content)
