import cv2
import face_recognition
import shutil

from app.constants import FACES_DIR, QUERIES_DIR, TMP_DIR
from app.models.identities import Identity
from app.models.recognition import FaceEncoding, Query, Suggestion
from app.schemas.recognition import Recognition
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Tuple
from uuid import uuid4, UUID


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
    def get_faces_locations(cls, image) -> List[tuple[int, int, int, int]]:
        """
        Return faces locations on an image
        """
        return face_recognition.face_locations(image)

    @classmethod
    def create_face_encoding(cls, db: Session, identity: Identity, image, rect: Tuple[int, int, int, int]) -> FaceEncoding:
        """
        Store known face in database
        """
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
    def query(cls, db: Session, image: Any, faces: List[tuple[int, int, int, int]]) -> List[Recognition]:
        """
        Create a new query in database
        """
        query = Query()

        db.add(query)
        db.flush()

        query_dir = QUERIES_DIR / str(query.id)

        if not query_dir.exists():
            query_dir.mkdir(parents=True)

        # Store the full image
        if not cv2.imwrite(str(query_dir / 'full.png'), image):
            raise Exception('Unable to write query full image')

        result = []

        for (top, right, bottom, left) in faces:
            recognition = cls.identify(db, image, (top, right, bottom, left))

            if recognition:
                result.append(recognition)

            suggestion = Suggestion()
            suggestion.query_id = query.id
            suggestion.rect = [top, right, bottom, left]

            if recognition:
                suggestion.identity_id = recognition.identity.id
                suggestion.score = recognition.score

            db.add(suggestion)
            db.flush()

            # Write the suggestion file
            if not cv2.imwrite(str(query_dir / f'{suggestion.id}.png'), image[top:bottom, left:right]):
                raise Exception('Unable to write suggestion image')

        db.commit()

        return result

    @classmethod
    def get_queries(cls, db: Session) -> List[Query]:
        """
        Get queries in database
        """
        return db.query(Query).order_by(Query.created_at.asc()).all()

    @classmethod
    def get_query(cls, db: Session, id: UUID) -> Query:
        return db.query(Query).filter_by(id=id).one()

    @classmethod
    def get_suggestion(cls, db: Session, query_id: UUID, suggestion_id: UUID) -> Suggestion:
        return db.query(Suggestion).filter_by(query_id=query_id, id=suggestion_id).one()

    @classmethod
    def confirm_suggestion(cls, db: Session, query_id: UUID, suggestion_id: UUID, identity: Optional[Identity] = None) -> FaceEncoding:
        suggestion = cls.get_suggestion(db, query_id, suggestion_id)
        suggestion_file = QUERIES_DIR / str(suggestion.query.id) / (str(suggestion.id) + '.png')

        if not suggestion_file.exists():
            raise Exception('Face file not found')

        image = cv2.imread(str(suggestion_file))
        identity = identity if identity else suggestion.identity
        encoding = cls.create_face_encoding(db, identity, image, (0, image.shape[1], image.shape[0], 0))

        cls.delete_suggestion(db, query_id, suggestion_id)

        return encoding

    @classmethod
    def delete_suggestion(cls, db: Session, query_id: UUID, suggestion_id: UUID) -> None:
        suggestion = cls.get_suggestion(db, query_id, suggestion_id)
        query = suggestion.query

        db.delete(suggestion)
        db.flush()

        suggestion_file = QUERIES_DIR / str(suggestion.query.id) / (str(suggestion.id) + '.png')

        if not query.suggestions:
            if suggestion_file.parent.exists():
                shutil.rmtree(suggestion_file.parent)
            db.delete(query)
        elif suggestion_file.exists():
            suggestion_file.unlink()

        db.commit()

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
            return Recognition(**{
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
            })

        return None
