import cv2
import time

from app.cameras import VideoStream
from app.models.cameras import Camera
from typing import Tuple


class NetworkStream(VideoStream):
    def __init__(self, camera: Camera, *args, **kwargs):
        super().__init__(camera.id, *args, **kwargs)
        self._camera = camera
        self._cap = None
        self._retry_delay = 1.0

    def get_size(self) -> Tuple[int, int]:
        return (
            int(self._cap.get(3)),
            int(self._cap.get(4))
        )

    def next(self):
        if not self._cap:
            self._logger.debug('Opening capture from URL %s', self._camera.url)
            self._cap = cv2.VideoCapture(self._camera.full_url)

        if not self._cap.isOpened():
            self._logger.error(
                'Unable to open capture from URL %s. Waiting %d seconds',
                self._camera.url,
                self._retry_delay
            )
            self._cap.release()
            self._cap = None

            try:
                if self._running:
                    time.sleep(self._retry_delay)
            finally:
                return False

        ret, frame = self._cap.read()

        if not ret:
            self._logger.error('Unable to read frame, reset connection')
            self._cap.release()
            self._cap = None
            return False

        return frame

    @property
    def camera_id(self) -> str:
        return str(self._camera.id)

    @property
    def camera_name(self) -> str:
        return self._camera.label
