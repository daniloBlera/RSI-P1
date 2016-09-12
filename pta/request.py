# -*- coding: utf-8 -*-
class Request:
    """Wrapper para o array de bits contendo uma mensagem de requisição do
    protocolo PTA.

    Formato:
    <SEQ_NUM> <COMMAND> <ARGS>

    obs.: os seus campos são armazenados como string literal.
    """
    seq_num = None
    command = None
    args = None

    def __init__(self, request):
        request_utf8 = request.decode(encoding='utf-8')
        request_list = request_utf8.split(sep=' ')
        message_length = len(request_list)

        self.seq_num = request_list[0]
        self.command = request_list[1]

        if message_length > 2:
            self.args = request_list[2]

    def __str__(self):
        return self.command

    def to_bytes(self):
        message = self.seq_num + ' ' + self.command + ' ' + self.args
        return str.encode(message)

    def is_cump_type(self):
        return self.command == 'CUMP'

    def is_list_type(self):
        return self.command == 'LIST'

    def is_pega_type(self):
        return self.command == 'PEGA'

    def is_term_type(self):
        return self.command == 'TERM'
