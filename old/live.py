#!/usr/bin/env python

import click
import cv2
import face_recognition
import logging

from pathlib import Path
from lib.database import Database


@click.command()
@click.option('-u', '--url', type=str, help='URL', required=True)
@click.option('-d/-D', '--debug/--no-debug', default=False, help='Enable debug messages')
@click.option('-l', '--log-file', default=None, help='Ouptut log file')
def live(url: str, debug: bool, log_file: str):
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(levelname)s - %(message)s',
        level=logging.DEBUG if debug else logging.INFO,
        filename=log_file,
    )
    logger = logging.getLogger('live')


    pgsql = Database('localhost', 5432, 'faces', 'faces', 'faces')
    pgsql.connect()

    logger.debug('Connected to postgresql')

    pgsql.close()

    cam = cv2.VideoCapture('rtsp://192.168.1.30:554/ch0_0.h264')

    ok = 0
    ko = 0

    while(True):
        ret, frame = cam.read()

        if ret:
            ok += 1
        else:
            ko += 1

        print(f'\rOK: {ok} - KO: {ko}')


    cam.release()

if __name__ == '__main__':
    live()
