import cv2
import face_recognition
import logging
import time

from app.controllers.recognition import RecognitionController
from sqlalchemy.orm import Session


class VideoStream:
    """
    Max image width used with face_recognition
    """
    max_width = 320

    def __init__(self, 
        db: Session,
        face_recognition: bool = True,
        recognition_interval: int = 1000,
        fps: int = 25,
        show_fps: bool= True,
        label: str = None,
        force_width: int = None
    ):
        self._logger = logging.getLogger(__name__)
        self._face_recognition = face_recognition
        self._db = db
        self._last_frame = None
        self._last_refresh = None
        self._refresh_delay = recognition_interval
        self._rectangles = []
        self._fps_limit = fps
        self._fps_show = show_fps
        self._fps_count = 0
        self._fps_time = None
        self._fps_value = None
        self._tick = 0
        self._label = label
        self._force_width = force_width

    def refresh_rectangles(self, frame) -> None:
        if frame.shape[1] > self.max_width:
            ratio = self.max_width / frame.shape[1]
            image = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
        else:
            ratio = 1
            image = frame

        locations = face_recognition.face_locations(image)
        rectangles = []

        for (top, right, bottom, left) in locations:
            encodings = face_recognition.face_encodings(image, known_face_locations=[(top, right, bottom, left)])

            if len(encodings) == 1:
                result = RecognitionController.identify(self._db, image, (top, right, bottom, left))
                if result:
                    label = result['identity'].first_name + ': ' + str(result['score'])
                else:
                    label = None
            else:
                label = None

            top = int(top / ratio)
            right = int(right / ratio)
            bottom = int(bottom / ratio)
            left = int(left / ratio)

            rectangles.append((
                (left, top),
                (right, bottom),
                label,
            ))

        self._rectangles = rectangles
        self._last_refresh = self._tick

    def draw_rectangles(self, frame):
        for rectangle in self._rectangles:
            frame = cv2.rectangle(frame, rectangle[0], rectangle[1], (255, 0, 0), 2)

            if rectangle[2]:
                frame = cv2.putText(frame, rectangle[2], (rectangle[0][0], rectangle[1][1] + 24), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0))

        return frame

    def show_fps(self, frame):
        self._fps_count += 1

        if self._fps_time is None:
            self._fps_time = self._tick
            return frame

        if self._tick - self._fps_time == 0:
            return frame

        if (self._tick - self._fps_time) >= 1000:
            self._fps_value = self._fps_count
            self._fps_count = 0
            self._fps_time = self._tick

        if self._fps_value is not None:
            frame = cv2.putText(frame, f'FPS: {self._fps_value}', (5, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 2555))

        return frame

    def limit_fps(self):
        delay = 1000.0 / float(self._fps_limit)

        if self._last_frame is not None and (self._tick - self._last_frame < delay):
            return False

        self._last_frame = self._tick

        return True

    def resize(self, frame):
        ratio = self._force_width / frame.shape[1]
        return ratio, cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)

    def read(self):
        raise NotImplementedError()

    def get_frame(self):
        self._tick = time.time_ns() / 1000000.0

        ret, frame = self.read()

        if not ret:
            return False, None

        if not self.limit_fps():
            return False, None

        if self._face_recognition:
            if self._last_refresh is None or (self._tick - self._last_refresh) >= self._refresh_delay:
                self.refresh_rectangles(frame)
            frame = self.draw_rectangles(frame)

        if self._force_width is not None:
            _, frame = self.resize(frame)

        if self._fps_show:
            frame = self.show_fps(frame)

        ret, jpeg = cv2.imencode('.jpg', frame)

        if not ret:
            self._logger.warning('Unable to convert frame to JPEG')
            return False, None

        return True, jpeg.tobytes()


class RtspStream(VideoStream):
    def __init__(self, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger.debug('Initializing RTSP video stream with URL %s', url)
        self._url = url
        self._stream = cv2.VideoCapture(url)

    def __str__(self):
        return f'RtspStream({self._url})'

    def __del__(self):
        self._logger.debug('Destroying RTSP video stream')
        self._stream.release()

    def read(self):
        ret, frame = self._stream.read()

        if not ret:
            self._logger.warning('Unable to read frame from RTSP stream')
            return False, None

        return ret, frame
