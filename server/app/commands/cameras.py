import signal

from app.cameras.handlers import RecognitionHandler, SocketHandler
from app.cameras.streams import NetworkStream
from app.commands import cli
from app.controllers.cameras import CameraController
from app.database import SessionLocal


@cli.group()
def cameras():
    pass


@cameras.command()
def run():
    # Intercept SIGINT and stop all threads
    def signal_handler(*args, **kwargs):
        for stream in streams:
            stream.stop()

    signal.signal(signal.SIGINT, signal_handler)

    # Fetch cameras
    db = SessionLocal()
    cameras = CameraController.get_cameras(db)
    db.close()

    # Start threads
    streams = tuple(NetworkStream(camera) for camera in cameras)

    for stream in streams:
        stream.add_handler(RecognitionHandler(stream, record=True), max_fps=1)
        stream.add_handler(SocketHandler(stream, max_width=800), max_fps=5)
        stream.start()

    # Wait end of the threads
    for stream in streams:
        stream.join()
