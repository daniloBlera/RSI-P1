# -*- coding: utf-8 -*-
class Response:
    """Wrapper para o array de bits contendo uma mensagem de resposta do
    protocolo PTA.

    Formato:
    <SEQ_NUM> <REPLY> <ARGS> <TAIL>
    """
    seq_num = None
    reply = None
    args = None
    tail = None

    def __init__(self, response):
        response_utf8 = response.decode(encoding='utf-8')
        response_list = response_utf8.split(sep=' ')
        message_length = len(response_list)

        self.seq_num = response_list[0]
        self.reply = response_list[1]

        if message_length > 3:
            self.args = response_list[2:message_length - 1]
            self.tail = response_list[message_length - 1]

    def __str__(self):
        return self.reply
