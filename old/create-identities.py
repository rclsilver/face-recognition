#!/usr/bin/env python

import click
import face_recognition
import logging

from pathlib import Path
from lib.database import Database


@click.command()
@click.option('-i', '--input-directory', type=Path, help='Input directory', required=True)
@click.option('-d/-D', '--debug/--no-debug', default=False, help='Enable debug messages')
@click.option('-l', '--log-file', default=None, help='Ouptut log file')
def create_identities(input_directory: Path, debug: bool, log_file: str):
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(levelname)s - %(message)s',
        level=logging.DEBUG if debug else logging.INFO,
        filename=log_file,
    )
    logger = logging.getLogger('create-identities')

    if not input_directory.exists():
        logger.fatal(f'Input directory "{input_directory}" does not exist')
        exit(1)

    pgsql = Database('localhost', 5432, 'faces', 'faces', 'faces')
    pgsql.connect()

    logger.debug('Connected to postgresql')

    for person in input_directory.iterdir():
        name = person.stem
        person_id = pgsql.get_or_create_person(name)

        for file in person.iterdir():
            logger.debug('Loading %s', file)
            image = face_recognition.load_image_file(str(file))

            for encoding in face_recognition.face_encodings(image):
                logger.info('New encoding found for %s (#%d)', name, person_id)
                pgsql.add_encoding(person_id, str(file), encoding)

    pgsql.close()

if __name__ == '__main__':
    create_identities()
