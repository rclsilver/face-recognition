import socket
import struct

from app.models.cameras import Camera
from app.cameras.handlers import SocketHandler


class SocketClientException(Exception):
    pass


class ConnectionClosed(SocketClientException):
    def __init__(self, *args, **kwargs):
        super().__init__('Connection closed', *args, **kwargs)


class SocketClient(object):
    def __init__(self, camera: Camera):
        self._camera = camera
        self._socket_file = SocketHandler.socket_file(camera)
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.connect(str(self._socket_file))

    def _read_bytes(self, size: int, buffer_size: int = 4096) -> bytes:
        buffer = b''
        remaining = size

        while remaining:
            data = self._socket.recv(buffer_size if remaining > buffer_size else remaining)

            if not data:
                raise ConnectionClosed()

            buffer += data
            remaining -= len(data)

        return buffer

    def _read_size(self) -> int:
        payload_size = struct.calcsize('>L')
        size_bytes = self._read_bytes(payload_size)
        return struct.unpack('>L', size_bytes)[0]

    def _read_jpeg(self, size: int) -> bytes:
        return self._read_bytes(size)

    def close(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        size = self._read_size()
        return self._read_jpeg(size)

    @property
    def camera(self):
        return self._camera
