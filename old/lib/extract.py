import cv2
import face_recognition
import logging

from pathlib import Path

class FaceExtractor:
    def __init__(self, output_directory: Path, max_width=320):
        self._output_directory = output_directory
        self._max_width = max_width
        self._logger = logging.getLogger(__name__)

    def analyze_image(self, file: Path) -> list[Path]:
        self._logger.debug('Loading image from "%s"', file)
        image = cv2.imread(str(file))
        frame = image
        ratio = 1

        if image.shape[1] > self._max_width:
            ratio = self._max_width / image.shape[1]
            frame = cv2.resize(image, (0, 0), fx=ratio, fy=ratio)

        face_locations = face_recognition.face_locations(frame)

        self._logger.debug('[%s] Found %d face(s)', file.name, len(face_locations))

        found_faces = []

        for idx, (top, right, bottom, left) in enumerate(face_locations):
            top = int(top / ratio)
            right = int(right / ratio)
            bottom = int(bottom / ratio)
            left = int(left / ratio)

            face = image[top:bottom, left:right]
            face_file = self._output_directory / (file.stem + '_' + str(idx + 1) + '.jpg')
            cv2.imwrite(str(face_file), face)
            self._logger.info('[%s] Written face #%d in "%s"', file.name, idx + 1, face_file)
            found_faces.append(face_file)

        return found_faces
