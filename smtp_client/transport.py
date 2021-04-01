from socket import socket, AF_INET, SOCK_STREAM
import ssl

from smtp_client.const import PORT_DEFAULT, ENCODING_DEFAULT


class Transport:
    def __init__(self, is_ssl: bool, server: str, chunk=1024):
        self._socket = socket(AF_INET, SOCK_STREAM)
        if is_ssl:
            self._socket = ssl.wrap_socket(self._socket)

        self._socket.connect(*self.parse_domain_name(server))
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
        if send_str is not bytes and send_str[-1] != '\n':
            send_str += '\n'
        self._socket.sendall(
            bytes(send_str, encoding=ENCODING_DEFAULT))

    def recv(self) -> bytes:
        data = bytearray()
        while True:
            temp = self._socket.recv(self._chunk)
            if not temp or temp == '' or temp == b'':
                break
            else:
                data += temp
        return bytes(data)

    def get_secure_socket(self):
        self._socket = ssl.create_default_context().wrap_socket(
            self._socket, server_hostname=self._server)
