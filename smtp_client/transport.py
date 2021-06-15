# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_STREAM
import ssl

from smtp_client.const import *


class Transport:
    def __init__(self, is_ssl: bool, server: str, chunk=1024):
        self._socket = socket(AF_INET, SOCK_STREAM)
        if is_ssl:
            self._socket = ssl.wrap_socket(self._socket)
        t = self.parse_domain_name(server)
        self._socket.connect(t)
        self._is_ssl = is_ssl
        self._chunk = chunk
        self._server = server

    @staticmethod
    def parse_domain_name(server: str) -> (str, int):
        arr = server.split(':')
        if len(arr) == 1:
            return arr[0], PORT_DEFAULT
        if len(arr) == 2:
            return arr[0], int(arr[1])
        # exception

    def send(self, send_str):
        if not isinstance(send_str, bytes) and send_str[-1] != '\n':
            send_str += '\n'
        if isinstance(send_str, bytes):
            self._socket.sendall(send_str)
        else:
            self._socket.sendall(
                bytes(send_str, encoding=ENCODING_DEFAULT))

    def recv(self) -> bytes:
        data = bytearray()
        temp = bytes()
        while not self.check_last_line(temp):
            temp = self._socket.recv(self._chunk)
            data += temp
        return bytes(data)

    def check_last_line(self, data: bytes):
        data = data.decode(encoding=ENCODING_DEFAULT)
        try:
            t = data.split(LINE_BREAK)[-2]
            if t[3] == ' ':
                return True
        except Exception:
            return False

    def get_secure_socket(self):
        self._socket.close()
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket = ssl.wrap_socket(self._socket)
        self._socket.connect((self.parse_domain_name
                              (self._server)[0], SECURE_PORT))
