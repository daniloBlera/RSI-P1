# -*- coding: utf-8 -*-
import os
import logging
import socket
import traceback

from pta.request import Request


class PTAServer:
    """Implementação de um servidor com protocolo PTA."""
    NOK = 'NOK'
    OK = 'OK'
    ARQS = 'ARQS'
    END = ':END:'

    # TODO colocar formato padrão nas respectivas classes
    """Formato de respostas."""
    cump_ok_response = "{0} OK"
    cump_nok_response = "{0} NOK"

    list_ok_response = "{} ARQS {} :END:"
    list_nok_response = "{} NOK"

    pega_ok_response = "{} ARQ {} :END:"
    pega_nok_response = "{} NOK"

    term_ok_response = "{} OK"
    term_nok_response = '{} NOK'

    nok_response = "{} NOK"

    command_list = ['CUMP', 'LIST', 'PEGA', 'TERM']

    # TODO adicionar lista de usuários
    user_list = ['user1', 'ayylien']

    def __init__(self, hostname='localhost', port=12000):
        """Instancia um servidor com o endereço de host e portas fornecidos."""
        self.address = (hostname, port)

        self.file_dir = '{0}/pta/arquivos/'.format(os.getcwd())
        file_list = os.listdir(self.file_dir)

        self.file_list = []
        self.file_list.append(file_list[0].strip('\n'))
        self.file_list.append(file_list[1].strip('\n'))

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(self.console_handler)

    def handle_list_request(self, request_obj):
        """Lida com requisições 'LIST'."""
        seq_num = request_obj.seq_num

        args = ','.join(self.file_list)
        return self.list_ok_response.format(seq_num, args)

    def handle_term_request(self, request_obj):
        """Lida com requisições 'TERM'."""
        seq_num = request_obj.seq_num

        return self.term_ok_response.format(seq_num)

    def get_pega_response_from(self, request_object):
        """Retorna uma resposta à requisição 'PEGA' como string literal.

        Possíveis retornos:

        <seq_num> NOK

        caso o arquivo pedido na requisição não exista ou

        <seq_num> ARQS <byte_array> :END:

        caso o arquivo exista, onde '<byte_array>' são os bytes do arquivo
        requisitado.
        """
        seq_num = request_object.seq_num
        filename = request_object.args

        self.logger.debug("----ARQUIVO SOLICITADO: %s",
                          filename)

        file_list = os.listdir(self.file_dir)

        if filename not in file_list:
            self.logger.debug(
                "----ARQUIVO NÃO ENCONTRADO: %s",
                filename)

            response = self.get_nok_response(seq_num)
        else:
            self.logger.debug(
                "----ARQUIVO ENCONTRADO: %s",
                filename)

            file_content = self.get_data_stream_from(
                filename)

            response = self.get_pega_ok_response(
                seq_num, file_content)

        return response

    def is_valid_user(self, username):
        """Verifica se o nome fornecido se encontra na lista de usuários."""
        return username in self.user_list

    def get_ok_response(self, seq_num):
        """Retorna uma resposta OK genérica no formato

        <seq_num> OK

        como string literal.
        """
        return self.cump_ok_response.format(seq_num)

    def get_nok_response(self, seq_num):
        """Retorna uma resposta 'NOK' genérica no formato

        <seq_num> NOK

        como um string literal.
        """
        return self.nok_response.format(seq_num)

    def get_pega_ok_response(self, seq_num, file_stream):
        """Retorna uma resposta 'OK' para a requisição PEGA no formato

        <seq_num> ARQ <file_stream> :END:

        como um string literal.
        """
        return self.pega_ok_response.format(seq_num, file_stream)

    def get_data_stream_from(self, filename):
        """Retorna o arquivo de nome 'filename' como um array de bytes."""
        file_path = "{0}/{1}".format(self.file_dir, filename)
        file = open(file_path, 'r')
        stream = file.read()
        file.close()
        return stream

    def handle_user_session(self, connection_socket):
        """Lida com as requisições durante a sessão do usuário.

        Requisições:
        CUMP - retorna <seq_num> NOK

        LIST - retorna <seq_num> ARQS <files,separated,by,comma> :END:
                        ou <seq_num> OK/NOK

        PEGA - retorna <seq_num> ARQ <byte_stream> :END:
                        ou <seq_num> NOK

        TERM - retorna <seq_num> OK e fecha a conexão atual do socket.
        """
        session_is_open = True
        while session_is_open:
            session_message = connection_socket.recv(2048)

            if not session_message:
                self.logger.debug(
                    "----SOCKET CLIENTE FECHADO--")
                break

            session_request = Request(session_message)
            if session_request.is_list_type():
                self.logger.debug(
                    "----LIST RECEBIDO: %s",
                    session_message.decode("utf-8"))

                response = self.handle_list_request(
                    session_request)

            elif session_request.is_term_type():
                self.logger.debug(
                    "----TERM RECEBIDO: %s",
                    session_message.decode("utf-8"))

                response = self.get_ok_response(
                    session_request.seq_num)

                session_is_open = False

            elif session_request.is_cump_type():
                self.logger.debug(
                    "----CUMP RECEBIDO DENTRO DE SESSÃO: %s",
                    session_message.decode("utf-8"))

                response = self.get_nok_response(
                    session_request.seq_num)

            elif session_request.is_pega_type():
                self.logger.debug(
                    "----PEGA RECEBIDO: %s",
                    session_message.decode("utf-8"))

                response = self.get_pega_response_from(session_request)

            self.logger.debug(
                "----->RESPOSTA DA REQUISIÇÃO: %s", response)
            connection_socket.sendall(str.encode(response))

    def start_listening(self):
        """Escuta indefinidamente por requisições, a sua execução é blocante.

        obs.: pode ser parado com KeyboardInterrupt.
        """
        server_socket = socket.socket(family=socket.AF_INET,
                                      type=socket.SOCK_STREAM)

        server_socket.bind(self.address)
        server_socket.listen(1)

        self.logger.debug("DIRETÓRIO DOS ARQUIVOS:\n%s\n", self.file_dir)
        self.logger.debug("ARQUIVOS:\n%s\n", os.listdir(path=self.file_dir))
        self.logger.warn("--Servidor escutando requisições--\n")

        # Lida com as requisições inicias durante o período de apresentação
        # antes de abrir uma sessão.
        listening_tcp_requests = True
        while listening_tcp_requests:
            try:
                connection_socket, address = server_socket.accept()
                self.logger.debug("--Conexão TCP aceita--")

                message = connection_socket.recv(2048)
                request_obj = Request(message)

                self.logger.debug("--Requisição PTA recebida: %s",
                                 message.decode('utf-8'))

                if request_obj.is_cump_type():
                    self.logger.debug("--CUMP RECEBIDO--")

                    client_username = request_obj.args
                    if self.is_valid_user(client_username):
                        self.logger.debug("--USUÁRIO VÁLIDO--")

                        cump_ok = self.get_ok_response(request_obj.seq_num)
                        connection_socket.sendall(str.encode(cump_ok))

                        # Inicia uma sessão com o usuário após o recebimento de
                        # um CUMP contendo um nome de usuário válido.
                        self.logger.debug("##INICIANDO SESSÃO##")
                        self.handle_user_session(connection_socket)
                        self.logger.debug("##FINALIZANDO SESSÃO##")
                    else:
                        self.logger.debug("--USUÁRIO INVÁLIDO NO CUMP--")
                        response = self.get_nok_response(request_obj.seq_num)
                        connection_socket.sendall(str.encode(response))

                else:
                    if request_obj.command not in self.command_list:
                        self.logger.debug("--REQUISIÇÃO COM COMMAND INVÁLIDO--")
                        response = self.get_nok_response(request_obj.seq_num)
                    else:
                        self.logger.debug(
                            "--REQUISIÇÃO NÃO-CUMP RECEBIDA FORA DE SESSÃO--")

                        response = self.get_nok_response(request_obj.seq_num)

                    connection_socket.sendall(str.encode(response))

                self.logger.debug("\n--Fechando Socket--")
                connection_socket.close()
                self.logger.debug("--Socket fechado--\n")
            except KeyboardInterrupt:
                break
            except Exception:
                traceback.print_exc()
                break

        server_socket.close()
        self.logger.warn("--Escuta de requisições do servidor encerrada--")
