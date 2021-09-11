import cv2
import datetime
import face_recognition
import select
import socket
import struct

from app.cameras import BaseThread, FrameHandler, VideoStream
from app.controllers.recognition import RecognitionController
from app.constants import SOCKET_DIR
from app.database import SessionLocal
from app.models.cameras import Camera
from datetime import datetime
from pathlib import Path
from typing import Union


class RecognitionHandler(FrameHandler):
    def __init__(
        self,
        stream: VideoStream,
        max_width: float = 320.0,
        record: bool = False,
        record_timeout: int = 30,
        record_increase_timeout: int = 15,
    ):
        super().__init__(stream, max_queue_size=0)

        self._max_width = max_width
        self._db = SessionLocal()
        self._record = record
        self._record_timeout = record_timeout
        self._record_increase_timeout = record_increase_timeout

    def __del__(self):
        self._db.close()

    def process(self, frame: any):
        # Resize the frame if required
        if frame.shape[1] > self._max_width:
            ratio = self._max_width / frame.shape[1]
            image = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
        else:
            ratio = 1
            image = frame
        self._tracker.add('Resize')

        # Fetch locations
        locations = face_recognition.face_locations(image)
        self._tracker.add('Fetch locations')

        if len(locations):
            # Start recording if locations found
            if self._record:
                if not self._stream.recording:
                    self._stream.start_record(self._record_timeout)
                else:
                    self._stream.increase_record(self._record_increase_timeout)

            # Fetch identities
            result = RecognitionController.query(self._db, image, locations)

            for recognition in result.recognitions:
                if recognition.identity:
                    self._logger.debug('Found %s with score of %.02f %%', recognition.identity.first_name, recognition.score)
                else:
                    self._logger.debug('Found unknown person')
            self._tracker.add('Identify')

        self._tracker.show_inline(fn=self._logger.debug)


class StreamServer(BaseThread):
    def __init__(self, socket_file: Path):
        super().__init__(name=str(socket_file))

        if not socket_file.parent.exists():
            self._logger.debug('Creating streams directory %s', socket_file.parent)
            socket_file.parent.mkdir(parents=True)

        self._socket_file = socket_file
        self._socket = None
        self._clients = []

    def __del__(self):
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass

        if self._socket_file.exists():
            self._logger.debug('Deleting socket %s', self._socket_file)
            self._socket_file.unlink()

    def start(self):
        if self._running:
            raise Exception('Server already running')

        # Listening
        self._clients = []
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(str(self._socket_file))
        self._socket.listen(0)

        # Starting the thread
        return super().start()

    def stop(self):
        super().stop()

        # Shutdown the socket
        self._socket.shutdown(socket.SHUT_RDWR)

    def run(self):
        while self._running:
            read_socks, _, _ = select.select(self._clients + [self._socket], [], [])

            for sock in read_socks:
                if sock == self._socket:
                    # Server socket
                    try:
                        client, _ = sock.accept()
                        self._logger.debug('New connection')
                        self._clients.append(client)
                    except OSError:
                        continue
                else:
                    # Client socket
                    data = b''

                    try:
                        data = sock.recv(1024)
                    except OSError:
                        pass

                    if not data:
                        self._logger.debug('Client disconnected')
                        self._clients.remove(sock)

        # Close the server socket
        self._socket.close()
        self._socket = None

        # Close all clients connections
        for client in self._clients:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        self._clients = []

    def send_to_clients(self, jpeg_bytes):
        size = len(jpeg_bytes)
        data = struct.pack('>L', size) + jpeg_bytes

        for client in self._clients:
            try:
                client.sendall(data)
            except OSError:
                pass

    @property
    def clients(self):
        return self._clients


class SocketHandler(FrameHandler):
    @classmethod
    def socket_file(cls, src: Union[VideoStream, Camera]) -> Path:
        if isinstance(src, VideoStream):
            id = src.camera_id
        elif isinstance(src, Camera):
            id = str(src.id)
        else:
            raise TypeError('src')

        return SOCKET_DIR / f'{id}.sock'

    def __init__(self, stream: VideoStream, max_width: int = 0):
        super().__init__(stream, max_queue_size=1)

        self._server = StreamServer(self.socket_file(stream))
        self._max_width = max_width

    def start(self) -> None:
        self._server.start()
        return super().start()

    def run(self):
        super().run()

        self._server.stop()
        self._server.join()

    def process(self, frame: any):
        if self._server.clients:
            frame = frame.copy()
            self._tracker.add('Copy frame')

            if self._max_width > 0 and frame.shape[1] > self._max_width:
                ratio = self._max_width / frame.shape[1]
                frame = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
                self._tracker.add('Resize frame')

            font = cv2.FONT_HERSHEY_COMPLEX
            scale = 1.5
            thickness = 2
            color = (255, 255, 255)
            margin = 5

            name = self._stream.camera_name
            name_size = cv2.getTextSize(name, font, scale, thickness)
            name_pos = (margin, name_size[0][1] + margin)

            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_pos = (margin, frame.shape[0] - margin)

            cv2.putText(frame, name, name_pos, font, scale, color, thickness)
            cv2.putText(frame, date, date_pos, font, scale, color, thickness)
            self._tracker.add('Add text')

            ret, jpeg = cv2.imencode('.jpg', frame)
            self._tracker.add('Encode to JPEG')

            if ret:
                # send jpeg.tobytes() to all clients
                self._server.send_to_clients(jpeg.tobytes())
                self._tracker.add('Send to clients')

            self._tracker.show_inline(fn=self._logger.debug)
