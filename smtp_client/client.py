# -*- coding: utf-8 -*-

import sys
from base64 import b64decode
from typing import Deque
from collections import deque

from smtp_client.const import *
import smtp_client.message
import smtp_client.transport


class Client:
    def __init__(self, is_ssl: bool, server: str,
                 to_email: str, from_email: str,
                 verbose: bool,
                 login: bytes, password: bytes):
        self._transport = smtp_client.transport.Transport(is_ssl, server)
        self._pipeline = False
        self._login = login
        self._password = password
        self._verbose = verbose
        self._from_email = from_email
        self._to_email = to_email
        self._max_size = float('inf')
        self._features = set()

    def auth(self):
        self.send_command(deque([
            'AUTH LOGIN',
            self._login.decode(),
            self._password.decode()]))

    def send_command(self, commands: Deque):
        self._transport.send(commands.popleft())
        if self._pipeline:
            self._transport.send(self.get_str_commands(commands))
        self.print(self._transport.recv())
        if not self._pipeline:
            while len(commands) > 0:
                self._transport.send(commands.popleft())
                self.print(self._transport.recv())

    @staticmethod
    def get_str_commands(commands: Deque) -> bytes:
        temp = ''
        for com in commands:
            temp += f'{com}{LINE_BREAK}'
        return bytes(temp, encoding=ENCODING_DEFAULT)

    def start_tls(self):
        def split_at_char(message_bytes, character, remove_CRLF):
            halves = message_bytes.split(character)
            if b'\r\n' in halves[0] and remove_CRLF:
                return halves[0], halves[1][0: len(halves[1]) - 2]
            else:
                return halves[0], halves[1]

        self._transport.send('STARTTLS')
        data = self._transport.recv()
        response_code, response_body = split_at_char(data, b" ", True)
        if not response_code.startswith(b'2'):
            print(response_code)
            raise Exception('Invalid server response to login authentication')
        self._transport.get_secure_socket()
        self.ehlo()

    def print(self, msg: bytes):
        if self._verbose:
            #p = b64decode(msg)
            sys.stdout.write(msg.decode())

    def send_mail(self, msg):
        self.send_command(deque([f'MAIL FROM: {self._from_email}{LINE_BREAK}',
                          f'RCPT TO: {self._to_email}{LINE_BREAK}',
                          f'DATA',
                          str(msg),
                          f'.{LINE_BREAK}']))

    def ehlo(self):
        self._transport.send(f'EHLO {NAME_CLIENT}')
        data = self._transport.recv().decode(encoding=ENCODING_DEFAULT)
        if self._verbose:
            sys.stdout.write(data)
        self.get_server_features(data)

    def get_server_features(self, data: str):
        for line in data.split(LINE_BREAK):
            code = line[0:3]
            annotation = line[4:]
            arr = annotation.split(' ')
            if code.startswith('2'):
                self._features.add(arr[0].lower())
            if annotation.startswith('SIZE'):
                if len(arr) > 1:
                    self._max_size = int(arr[1])
                else:
                    self._transport.send('SIZE')
                    data = self._transport.recv().decode(encoding=ENCODING_DEFAULT)
                    temp = data.split(' ')
                    self._max_size = int(temp[1])
                    # проверить как работает на сервере

            if annotation.startswith('PIPELINING'):
                self._pipeline = True

    def get_max_size(self):
        return self._max_size
