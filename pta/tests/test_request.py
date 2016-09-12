# -*- coding: utf-8 -*-
import unittest

from pta.request import Request


class TestRequestObject(unittest.TestCase):
    def test_request_constructor_with_full_parameters(self):
        seq_num = 'SEQ_NUM'
        command = 'COMMAND'
        args = 'ARGS'

        binary_request = b'SEQ_NUM COMMAND ARGS'
        request_object = Request(binary_request)

        self.assertEqual(request_object.seq_num, seq_num)
        self.assertEqual(request_object.command, command)
        self.assertEqual(request_object.args, args)

    def test_request_constructor_with_CUMP_request(self):
        seq_num = 'SEQ_NUM'
        command = 'CUMP'

        binary_request = b'SEQ_NUM CUMP'
        request_object = Request(binary_request)

        self.assertEqual(request_object.seq_num, seq_num)
        self.assertEqual(request_object.command, command)
        self.assertIsNone(request_object.args)

    # TODO implementar formato padrão de respostas
    # def test_cump_request_format(self):
    #     expected = '{0} CUMP {1}'
    #
    #     self.assertEqual(Request.cump_request, expected)
    #
    # def test_list_request_format(self):
    #     expected = '{0} LIST'
    #
    #     self.assertEqual(Request.cump_request, expected)
    #
    # def test_pega_request_format(self):
    #     expected = '{0} PEGA {1}'
    #
    #     self.assertEqual(Request.cump_request, expected)
    #
    # def test_term_request_format(self):
    #     expected = '{0} CUMP'
    #
    #     self.assertEqual(Request.cump_request, expected)
