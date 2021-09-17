import cv2
import logging
import queue
import time
import threading

from app.constants import RECORDS_DIR
from app.utils.time import TimeTracker
from datetime import datetime
from typing import Any, Tuple


class BaseThread(threading.Thread):
    def __init__(self, name: str):
        super().__init__(name=name)

        self._running = None
        self._logger = logging.getLogger('{}.{}({})'.format(
            __name__,
            self.__class__.__name__,
            self.name
        ))
        self._tracker = TimeTracker()

    def start(self) -> None:
        self._logger.debug('Starting the thread')
        self._running = True
        return super().start()

    def stop(self):
        self._logger.debug('Stopping the thread')
        self._running = False


class FrameHandler(BaseThread):
    def __init__(self, stream: 'VideoStream', max_queue_size: int = 0):
        super().__init__(name=stream.camera_id)

        self._queue = queue.Queue(max_queue_size)
        self._stream = stream

    def __str__(self) -> str:
        return '{}({})'.format(
            self.__class__.__name__,
            self.name
        )

    def process(self, frame: any):
        pass

    def run(self):
        while self._running or not self._queue.empty():
            try:
                frame = self._queue.get(block=True, timeout=1)
                self._tracker.reset()
                self.process(frame)
            except queue.Empty:
                pass
            except Exception as e:
                self._logger.exception('Uncaught exception')

    def add(self, frame):
        try:
            self._queue.put_nowait(frame.copy())
        except queue.Full:
            pass


class VideoStream(BaseThread):
    RECORD_EXTENSION = 'webm'

    def __init__(self, name: str):
        super().__init__(name=name)

        self._handlers = []
        self._last_frame = 0
        self._record = None
        self._record_timeout = 0
        self._record_size = None
        self._record_codec = 'VP80'
        self._record_extension = self.RECORD_EXTENSION
        self._fps_timestamp = 0
        self._fps_count = 0
        self._fps_avg = 0

    def add_handler(self, handler: FrameHandler, max_fps: int = 0) -> FrameHandler:
        self._handlers.append({
            'handler': handler,
            'delay': 1000.0 / max_fps if max_fps > 0 else 0.0,
            'last': 0,
        })
        return handler

    def start(self) -> None:
        for handler in self._handlers:
            handler['handler'].start()
        return super().start()

    def next(self) -> Any:
        raise NotImplementedError()

    def get_size(self) -> Tuple[int, int]:
        raise NotImplementedError()

    @property
    def camera_id(self) -> str:
        raise NotImplementedError()

    @property
    def camera_name(self) -> str:
        raise NotImplementedError()

    @property
    def avg_fps(self) -> int:
        return self._fps_avg

    def recorded_frame(self, frame):
        frame = frame.copy()

        font = cv2.FONT_HERSHEY_COMPLEX
        scale = 1.5
        thickness = 2
        color = (255, 255, 255)
        margin = 5

        name = self.camera_name
        name_size = cv2.getTextSize(name, font, scale, thickness)
        name_pos = (margin, name_size[0][1] + margin)

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_pos = (margin, frame.shape[0] - margin)

        cv2.putText(frame, name, name_pos, font, scale, color, thickness)
        cv2.putText(frame, date, date_pos, font, scale, color, thickness)

        return frame

    def run(self):
        while self._running:
            self._tracker.reset()

            try:
                frame = self.next()
                self._tracker.add('Read frame')

                # Compute avg fps
                now = self._tracker.now()
                self._fps_count += 1

                if not self._fps_timestamp or (now - self._fps_timestamp) >= 1000:
                    self._fps_avg = self._fps_count
                    self._fps_timestamp = now
                    self._fps_count = 0

                if self._record:
                    if self._record_timeout <= datetime.now().timestamp():
                        self.stop_record()

                if frame is not False:
                    if self._record_size is None:
                        self._record_size = self.get_size()

                    if self._record:
                        self._record.write(
                            self.recorded_frame(frame)
                        )
                        self._tracker.add('Record')

                    now = time.time_ns() / 1e6

                    for handler in self._handlers:
                        if now - handler['last'] >= handler['delay']:
                            handler['last'] = now
                            handler['handler'].add(frame)
                        self._tracker.add('Handler {}'.format(handler['handler']))
                
                self._tracker.show_inline(fn=self._logger.debug)
            except Exception:
                self._logger.exception('Uncaught exception')

        # Stopping handlers threads
        for handler in self._handlers:
            handler['handler'].stop()
            handler['handler'].join()

        # Stop the record
        if self.recording:
            self.stop_record()

    def start_record(self, timeout: int = 30):
        self._logger.info('Starting record')

        file = RECORDS_DIR / self.camera_id / '{}.{}'.format(
            datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
            self._record_extension
        )

        if not file.parent.exists():
            file.parent.mkdir(parents=True)

        # Compute FPS by speedup the video with a ratio of 2
        fps = self.avg_fps * 2 if self.avg_fps else 30

        self._record = cv2.VideoWriter(
            str(file),
            cv2.VideoWriter_fourcc(*self._record_codec),
            fps,
            self._record_size
        )
        self.increase_record(timeout)

    def increase_record(self, timeout: int = 30):
        self._logger.debug('Increase record timeout: %d', timeout)
        self._record_timeout = max(
            self._record_timeout,
            datetime.now().timestamp() + timeout
        )

    def stop_record(self):
        self._logger.info('Stopping record')
        self._record.release()
        self._record = None
        self._record_timeout = 0

    @property
    def recording(self):
        return self._record is not None
