#!/usr/bin/env python

import click
import logging

from pathlib import Path
from lib.extract import FaceExtractor


@click.command()
@click.option('-i', '--input-directory', type=Path, help='Input directory', required=True)
@click.option('-o', '--output-directory', type=Path, help='Output directory', required=True)
@click.option('-d/-D', '--debug/--no-debug', default=False, help='Enable debug messages')
@click.option('-l', '--log-file', default=None, help='Ouptut log file')
def extract(input_directory: Path, output_directory: Path, debug: bool, log_file: str):
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(levelname)s - %(message)s',
        level=logging.DEBUG if debug else logging.INFO,
        filename=log_file,
    )
    logger = logging.getLogger('extract-faces')

    if not input_directory.exists():
        logger.fatal(f'Input directory "{input_directory}" does not exist')
        exit(1)

    if not output_directory.exists():
        logger.debug(f'Creating output directory "{output_directory}"...')
        output_directory.mkdir(parents=True)

    extractor = FaceExtractor(output_directory)

    for file in list(input_directory.rglob('*.jpg')) + list(input_directory.rglob('*.png')):
        face_files = extractor.analyze_image(file)

        for face_file in face_files:
            logger.info('Face written in "%s"', face_file)


if __name__ == '__main__':
    extract()
