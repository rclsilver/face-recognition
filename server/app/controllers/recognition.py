import base64
import cv2
import face_recognition
import logging
import shutil
import uuid

from app.constants import FACES_DIR, QUERIES_DIR, TMP_DIR
from app.models.identities import Identity
from app.models.recognition import FaceEncoding, Query, Suggestion
from app.schemas.recognition import QueryResult, Recognition
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Tuple


logger = logging.getLogger(__name__)


class RecognitionException(Exception):
    pass


class NoEncodingFoundException(RecognitionException):
    def __init__(self):
        super().__init__('No encoding found')


class MultipleEncodingFoundException(RecognitionException):
    def __init__(self):
        super().__init__('More than one encoding found')


class RecognitionController:
    @classmethod
    def load_uploaded_file(cls, file: UploadFile) -> Any:
        # TODO do it without temp file ?
        new_uuid = str(uuid.uuid4())
        temp_file = TMP_DIR / f'{new_uuid}-{file.filename}'

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
    def create_face_encoding(cls, db: Session, identity: Identity, image, rect: Tuple[int, int, int, int], encoding: Optional[List[float]] = None) -> FaceEncoding:
        """
        Store known face in database
        """
        if encoding is None:
            encodings = face_recognition.face_encodings(image, known_face_locations=[rect])

            if not encodings:
                raise NoEncodingFoundException()
            elif len(encodings) > 1:
                raise MultipleEncodingFoundException()

            encoding = list(float(s) for s in encodings[0])

        result = FaceEncoding()
        result.identity_id = identity.id
        result.vec_low =  encoding[0:64]
        result.vec_high = encoding[64:128]

        db.add(result)
        db.flush()

        top, right, bottom, left = rect
        face = image[top:bottom, left:right]
        face_file = FACES_DIR / str(identity.id) / (str(result.id) + '.png')

        if not face_file.parent.exists():
            face_file.parent.mkdir(parents=True)

        if not cv2.imwrite(str(face_file), face):
            raise RecognitionException('Unable to write face file')

        db.commit()

        return result

    @classmethod
    def query(cls, db: Session, image: Any, faces: List[tuple[int, int, int, int]], confidence_threshold: float = 0.6, returns_picture: bool = False) -> QueryResult:
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
            db.rollback()
            raise RecognitionException('Unable to write query full image')

        result = {
            'recognitions': [],
            'picture': None
        }

        for (top, right, bottom, left) in faces:
            recognition, encoding = cls.identify(db, image, (top, right, bottom, left))
            result['recognitions'].append(recognition)

            # Record the query only if identity is not found or if score is below the confidence threshold
            if recognition.score is None or recognition.score < confidence_threshold:
                suggestion = Suggestion()
                suggestion.query_id = query.id
                suggestion.rect = [top, right, bottom, left]
                suggestion.vec_low = encoding[0:64]
                suggestion.vec_high = encoding[64:128]

                if recognition.identity:
                    suggestion.identity_id = recognition.identity.id
                    suggestion.score = recognition.score

                db.add(suggestion)
                db.flush()

                # Write the suggestion file
                if not cv2.imwrite(str(query_dir / f'{suggestion.id}.png'), image[top:bottom, left:right]):
                    raise RecognitionException('Unable to write suggestion image')

        if query.suggestions:
            # Commit the query and suggestions
            db.commit()
        else:
            # Delete the query without suggestion
            db.rollback()
            shutil.rmtree(query_dir)

        # Build the result image
        if returns_picture:
            if image.shape[1] > 640:
                ratio = 640 / image.shape[1]
                image = cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
            else:
                ratio = 1

            font = cv2.FONT_HERSHEY_COMPLEX
            scale = 1
            thickness = 1
            margin = 5
            color_found = (0, 255, 0)
            color_not_found = (0, 0, 255)

            for recognition in result['recognitions']:
                rect_start = (
                    int(recognition.rect.start.x * ratio),
                    int(recognition.rect.start.y * ratio),
                )
                rect_end = (
                    int(recognition.rect.end.x * ratio),
                    int(recognition.rect.end.y * ratio),
                )
                cv2.rectangle(image, rect_start, rect_end, color_found if recognition.identity else color_not_found, thickness)

                if recognition.identity:
                    rect_width = rect_end[0] - rect_start[0]

                    name = '{} {}.'.format(
                        recognition.identity.first_name,
                        recognition.identity.last_name[0]
                    )
                    name_size = cv2.getTextSize(name, font, scale, thickness)[0]
                    name_pos = (
                        int(rect_start[0] + (rect_width - name_size[0]) / 2),
                        rect_end[1] + name_size[1] + margin
                    )

                    score = '{}%'.format(int(recognition.score * 100))
                    score_size = cv2.getTextSize(score, font, scale * .8, thickness)[0]
                    score_pos = (
                        int(rect_start[0] + (rect_width - score_size[0]) / 2),
                        name_pos[1] + score_size[1] + margin
                    )

                    cv2.putText(image, name, name_pos, font, scale, color_found, thickness)
                    cv2.putText(image, score, score_pos, font, scale * .8, color_found, thickness)

            ret, jpeg = cv2.imencode('.jpg', image)

            if ret:
                result['picture'] = 'data:image/jpeg;base64,{}'.format(
                    base64.b64encode(
                        jpeg.tobytes()
                    ).decode('utf-8')
                )

        return QueryResult(**result)

    @classmethod
    def get_queries(cls, db: Session) -> List[Query]:
        """
        Get queries in database
        """
        return db.query(Query).order_by(Query.created_at.asc()).all()

    @classmethod
    def get_query(cls, db: Session, id: uuid.UUID) -> Query:
        return db.query(Query).filter_by(id=id).one()

    @classmethod
    def get_suggestions(cls, db: Session) -> List[Suggestion]:
        return db.query(Suggestion).all()

    @classmethod
    def get_suggestion(cls, db: Session, query_id: uuid.UUID, suggestion_id: uuid.UUID) -> Suggestion:
        return db.query(Suggestion).filter_by(query_id=query_id, id=suggestion_id).one()

    @classmethod
    def confirm_suggestion(cls, db: Session, query_id: uuid.UUID, suggestion_id: uuid.UUID, identity: Optional[Identity] = None) -> FaceEncoding:
        suggestion = cls.get_suggestion(db, query_id, suggestion_id)
        suggestion_file = QUERIES_DIR / str(suggestion.query.id) / f'{suggestion.id}.png'

        if not suggestion_file.exists():
            raise RecognitionException('Face file not found')

        image = cv2.imread(str(suggestion_file))
        identity = identity if identity else suggestion.identity

        if not identity:
            raise RecognitionException('No identity provided')

        encoding = cls.create_face_encoding(db, identity, image, (0, image.shape[1], image.shape[0], 0), suggestion.vec_low + suggestion.vec_high)

        cls.delete_suggestion(db, query_id, suggestion_id)

        return encoding

    @classmethod
    def delete_suggestion(cls, db: Session, query_id: uuid.UUID, suggestion_id: uuid.UUID) -> None:
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
    def clear_suggestions(cls, db: Session) -> None:
        """
        Clear all existing suggestions
        """
        for suggestion in db.query(Suggestion).all():
            cls.delete_suggestion(db, suggestion.query_id, suggestion.id)

    @classmethod
    def compute_suggestions(cls, db: Session, confidence_threshold: float = 0.6):
        """
        Recompute all existing suggestions
        """
        for suggestion in cls.get_suggestions(db):
            image_file = QUERIES_DIR / str(suggestion.query.id) / 'full.png'
            
            if not image_file.exists():
                logger.warning('No file found for suggestion %s: %s', suggestion.id, image_file)
                continue

            image = cv2.imread(str(image_file))
            new_prediction, _ = cls.identify(db, image, suggestion.rect)

            old_identity = suggestion.identity
            old_score = suggestion.score

            suggestion.identity_id = new_prediction.identity.id if new_prediction.identity else None
            suggestion.score = new_prediction.score
            db.commit()

            if suggestion.score is not None and suggestion.score >= confidence_threshold:
                # New prediction is relevant
                logger.info('Validating suggestion %s with a score of %.02f', suggestion.id, suggestion.score)
                cls.confirm_suggestion(db, suggestion.query_id, suggestion.id, suggestion.identity)
            else:
                # We update the suggestion
                logger.info(
                    'Updating suggestion %s: Identity[%s] -> Identity[%s] - Score[%.02f] -> Score[%.02f]',
                    suggestion.id,
                    f'{old_identity.first_name} {old_identity.last_name}' if old_identity else 'None',
                    f'{new_prediction.identity.first_name} {new_prediction.identity.last_name}' if new_prediction.identity else 'None',
                    old_score if old_score is not None else 0.0,
                    suggestion.score if suggestion.score is not None else 0.0,
                )

    @classmethod
    def identify(cls, db: Session, image, rect: Tuple[int, int, int, int], threshold: float = 0.6) -> Tuple[Recognition, List[float]]:
        """
        Identify face on a picture
        """
        encodings = face_recognition.face_encodings(image, known_face_locations=[rect])

        if not encodings:
            raise NoEncodingFoundException()
        elif len(encodings) > 1:
            raise MultipleEncodingFoundException()

        encoding = list(float(s) for s in encodings[0])

        row = db.execute(
            """
            SELECT identity_id, MIN(SQRT(POWER(CUBE(ARRAY[:vec_low]) <-> CUBE(vec_low), 2) + POWER(CUBE(ARRAY[:vec_high]) <-> CUBE(vec_high), 2))) AS score
            FROM face_encoding
            WHERE SQRT(POWER(CUBE(ARRAY[:vec_low]) <-> CUBE(vec_low), 2) + POWER(CUBE(ARRAY[:vec_high]) <-> CUBE(vec_high), 2)) <= :threshold
            GROUP BY 1
            ORDER BY 2 ASC
            LIMIT 1
            """, {
                'vec_low': encoding[0:64],
                'vec_high': encoding[64:128],
                'threshold': threshold,
            }
        ).fetchone()

        return Recognition(**{
            'identity': db.query(Identity).get(row[0]) if row else None,
            'score': 1 - row[1] if row else None,
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
        }), encoding
