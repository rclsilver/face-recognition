import cv2
import face_recognition

from app.constants import FACES_DIR, TMP_DIR
from app.models import FaceEncoding, Identity
from app.schemas import Recognition
from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Any, Tuple
from uuid import uuid4

class RecognitionController:
    @classmethod
    def load_uploaded_file(cls, file: UploadFile) -> Any:
        # TODO do it without temp file ?
        temp_file = TMP_DIR / str(str(uuid4()) + file.filename)

        if not TMP_DIR.exists():
            TMP_DIR.mkdir()

        with temp_file.open('wb') as f:
            content = file.file.read()
            f.write(content)
            f.flush()

        image = cv2.imread(str(temp_file))
        temp_file.unlink()

        return image

    @classmethod
    def get_faces_locations(cls, image):
        return face_recognition.face_locations(image)

    @classmethod
    def create_face_encoding(cls, db: Session, identity: Identity, image, rect: Tuple[int, int, int, int]) -> FaceEncoding:
        encodings = face_recognition.face_encodings(image, known_face_locations=[rect])

        if not encodings:
            raise Exception('No encoding found')
        elif len(encodings) > 1:
            raise Exception('More than one encoding found')

        result = FaceEncoding()
        result.identity_id = identity.id
        result.vec_low =  list(float(s) for s in encodings[0][0:64])
        result.vec_high = list(float(s) for s in encodings[0][64:128])

        db.add(result)
        db.flush()

        top, right, bottom, left = rect
        face = image[top:bottom, left:right]
        face_file = FACES_DIR / str(identity.id) / (str(result.id) + '.png')

        if not face_file.parent.exists():
            face_file.parent.mkdir(parents=True)

        if not cv2.imwrite(str(face_file), face):
            raise Exception('Unable to write face file')

        db.commit()

        return result

    @classmethod
    def identify(cls, db: Session, image, rect: Tuple[int, int, int, int], threshold: float = 0.6) -> Recognition:
        """
        Identify face on a picture
        """
        encodings = face_recognition.face_encodings(image, known_face_locations=[rect])

        if not encodings:
            raise Exception('No encoding found')
        elif len(encodings) > 1:
            raise Exception('More than one encoding found')

        row = db.execute(
            """
            SELECT identity_id, MIN(SQRT(POWER(CUBE(ARRAY[:vec_low]) <-> CUBE(vec_low), 2) + POWER(CUBE(ARRAY[:vec_high]) <-> CUBE(vec_high), 2))) AS score
            FROM face_encoding
            WHERE SQRT(POWER(CUBE(ARRAY[:vec_low]) <-> CUBE(vec_low), 2) + POWER(CUBE(ARRAY[:vec_high]) <-> CUBE(vec_high), 2)) <= :threshold
            GROUP BY 1
            ORDER BY 2 ASC
            LIMIT 1
            """, {
                'vec_low': list(float(s) for s in encodings[0][0:64]),
                'vec_high': list(float(s) for s in encodings[0][64:128]),
                'threshold': threshold,
            }
        ).fetchone()

        if row:
            return {
                'identity': db.query(Identity).get(row[0]),
                'score': 1 - row[1],
                'rect': {
                    'start': {
                        'x': rect[3],
                        'y': rect[0],
                    },
                    'end': {
                        'x': rect[1],
                        'y': rect[2],
                    },
                },
            }

        return None
