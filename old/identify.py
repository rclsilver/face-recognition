#!/usr/bin/env python

import click
import cv2
import face_recognition
import logging

from pathlib import Path
from lib.database import Database


@click.command()
@click.option('-i', '--input-file', type=Path, help='Input file', required=True)
@click.option('-d/-D', '--debug/--no-debug', default=False, help='Enable debug messages')
@click.option('-l', '--log-file', default=None, help='Ouptut log file')
def search_identity(input_file: Path, debug: bool, log_file: str):
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(levelname)s - %(message)s',
        level=logging.DEBUG if debug else logging.INFO,
        filename=log_file,
    )
    logger = logging.getLogger('identify')

    if not input_file.exists():
        logger.fatal(f'Input file "{input_file}" does not exist')
        exit(1)

    pgsql = Database('localhost', 5432, 'faces', 'faces', 'faces')
    pgsql.connect()

    logger.debug('Connected to postgresql')

    image = cv2.imread(str(input_file))

    if image.shape[1] > 320:
        ratio = 320 / image.shape[1]
        frame = cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
    else:
        ratio = 1
        frame = image

    encodings = face_recognition.face_encodings(frame)

    if not encodings:
        logger.warning('No face found on this picture')
    else:
        for encoding in encodings:
            result = pgsql.search_person(encoding)

            if result:
                name = pgsql.get_name(result[0])
                logger.info('Found person: %s (%f)', name, result[1])
            else:
                logger.warning('Person not found')

    pgsql.close()

if __name__ == '__main__':
    search_identity()
