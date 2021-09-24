from typing import Optional
import cv2
import pytest

from .. import database
from ..fixtures import identity, query
from ..test_data.identities import insert_identity
from ..test_data.recognition import insert_face_encoding, insert_suggestion
from app.constants import FACES_DIR, TMP_DIR, QUERIES_DIR
from app.controllers.recognition import RecognitionController, NoEncodingFoundException, MultipleEncodingFoundException, RecognitionException
from app.models.identities import Identity
from app.models.recognition import FaceEncoding, Query, Suggestion
from app.schemas.recognition import Recognition
from fastapi import UploadFile
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from unittest.mock import Mock, patch
from uuid import UUID
from typing import List, Optional


CHIRAC = Path(__file__).parent.parent / 'test_data' / 'images' / 'chirac.jpg'
CHIRAC_IMAGE = cv2.imread(str(CHIRAC))
CHIRAC_RECT = (0, CHIRAC_IMAGE.shape[1], CHIRAC_IMAGE.shape[0], 0)
OBAMA = Path(__file__).parent.parent / 'test_data' / 'images' / 'obama.jpg'
OBAMA_IMAGE = cv2.imread(str(OBAMA))
OBAMA_RECT = (0, OBAMA_IMAGE.shape[1], OBAMA_IMAGE.shape[0], 0)
DUMMY_ENCODING = list(float(i) for i in range(0, 128))


def build_identify_mock(encoding: List[float], identity: Optional[Identity] = None, score: Optional[float] = None):
    def mock(database: Session, image, rect):
        result = {
            'identity': identity,
            'score': score,
            'rect': {
                'start': {
                    'x': rect[3],
                    'y': rect[0],
                },
                'end': {
                    'x': rect[1],
                    'y': rect[2],
                }
            }
        }
        return Recognition(**result), encoding
    return mock

def build_image_mock(image_data = 'face-data', shape = (800, 800)):
    return Mock(__getitem__=lambda self, key: [image_data], shape=shape)

def cv2_imread_mock(filename: str):
    return build_image_mock()

def cv2_imwrite_mock(filename: str, data: list) -> bool:
    file = Path(filename)

    if not file.parent.exists():
        file.parent.mkdir(parents=True)

    file.open('wb').close()

    return True

def test_load_uploaded_file():
    with OBAMA.open('rb') as f:
        upload = UploadFile('obama.jpg', f, content_type='image/jpeg')
        temp_file = TMP_DIR / f'random-uuid-obama.jpg'

        with patch('uuid.uuid4', return_value='random-uuid'):
            with patch('cv2.imread', Mock()) as imread_mock:
                RecognitionController.load_uploaded_file(upload)
                imread_mock.assert_called_with(str(temp_file))

def test_get_faces_locations():
    with patch('face_recognition.face_locations', Mock()) as mock:
        mock.return_value = 'dummy-result'
        assert RecognitionController.get_faces_locations('dummy') == 'dummy-result'
        mock.assert_called_with('dummy')

def test_create_face_encoding_without_face():
    with pytest.raises(NoEncodingFoundException):
        with patch('face_recognition.face_encodings', return_value=None):
            RecognitionController.create_face_encoding(None, None, None, None)

def test_create_face_encoding_with_multiple_faces():
    with pytest.raises(MultipleEncodingFoundException):
        with patch('face_recognition.face_encodings', return_value=[None, None]):
            RecognitionController.create_face_encoding(None, None, None, None)

def test_create_face_encoding_but_unable_to_write_file(database: Session, identity: Identity):
    with patch('face_recognition.face_encodings', return_value=[DUMMY_ENCODING]):
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(RecognitionException) as e:
                RecognitionController.create_face_encoding(database, identity, OBAMA_IMAGE.copy(), OBAMA_RECT)
            assert e.value.args[0] == 'Unable to write face file'

def test_create_face_encoding(database: Session, identity: Identity):
    with patch('face_recognition.face_encodings', return_value=[DUMMY_ENCODING]):
        result = RecognitionController.create_face_encoding(database, identity, OBAMA_IMAGE.copy(), OBAMA_RECT)
        face_file = FACES_DIR / str(identity.id) / f'{result.id}.png'
        assert isinstance(result, FaceEncoding)
        assert result.id is not None
        assert result.identity_id == identity.id
        assert result.identity.id == identity.id
        assert result.vec_low == DUMMY_ENCODING[0:64]
        assert result.vec_high == DUMMY_ENCODING[64:128]
        assert face_file.exists()

def test_query_when_unable_to_write_full_image(database: Session):
    with pytest.raises(RecognitionException) as ei:
        with patch('cv2.imwrite', return_value=False):
            RecognitionController.query(database, None, None)
    assert ei.value.args[0] == 'Unable to write query full image'
    assert len(RecognitionController.get_queries(database)) == 0

def test_query_with_unknown_identity(database: Session):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)))):
        with patch('cv2.imread', side_effect=cv2_imread_mock):
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                result = RecognitionController.query(database, build_image_mock(), [(1, 2, 3, 4)])
                assert len(result.recognitions) == 1
                assert result.picture is None
                assert result.recognitions[0].identity is None
                assert result.recognitions[0].score is None
                assert result.recognitions[0].rect.start.x == 4
                assert result.recognitions[0].rect.start.y == 1
                assert result.recognitions[0].rect.end.x == 2
                assert result.recognitions[0].rect.end.y == 3
    assert len(RecognitionController.get_suggestions(database)) == 1

def test_query_with_known_identity_and_low_score(database: Session, identity: Identity):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)), identity, 0.5)):
        with patch('cv2.imread', side_effect=cv2_imread_mock):
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                result = RecognitionController.query(database, build_image_mock(), [(1, 2, 3, 4)])
                assert len(result.recognitions) == 1
                assert result.picture is None
                assert result.recognitions[0].identity is not None
                assert result.recognitions[0].identity.id == identity.id
                assert result.recognitions[0].score == 0.5
                assert result.recognitions[0].rect.start.x == 4
                assert result.recognitions[0].rect.start.y == 1
                assert result.recognitions[0].rect.end.x == 2
                assert result.recognitions[0].rect.end.y == 3
    assert len(RecognitionController.get_suggestions(database)) == 1

def test_query_with_known_identity_and_high_score(database: Session, identity: Identity):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)), identity, 0.8)):
        with patch('cv2.imread', side_effect=cv2_imread_mock):
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                result = RecognitionController.query(database, build_image_mock(), [(1, 2, 3, 4)])
                assert len(result.recognitions) == 1
                assert result.picture is None
                assert result.recognitions[0].identity is not None
                assert result.recognitions[0].identity.id == identity.id
                assert result.recognitions[0].score == 0.8
                assert result.recognitions[0].rect.start.x == 4
                assert result.recognitions[0].rect.start.y == 1
                assert result.recognitions[0].rect.end.x == 2
                assert result.recognitions[0].rect.end.y == 3
    assert len(RecognitionController.get_suggestions(database)) == 0

def test_query_and_return_image_without_resize(database: Session):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)))):
        with patch('cv2.imread', side_effect=cv2_imread_mock):
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                with patch('cv2.rectangle', return_value=True):
                    with patch('cv2.imencode', return_value=(True, Mock(tobytes=lambda: b'jpeg-data'))):
                        with patch('cv2.resize', return_value=build_image_mock(shape=(640, 640))) as resize_mock:
                            result = RecognitionController.query(database, build_image_mock(shape=(640, 640)), [(1, 2, 3, 4)], returns_picture=True)
                            assert len(result.recognitions) == 1
                            assert result.picture == 'data:image/jpeg;base64,anBlZy1kYXRh' # encoded version of 'jpeg-data'
                            resize_mock.assert_not_called()

def test_query_and_return_image_without_known_identity(database: Session):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)))):
        with patch('cv2.imread', side_effect=cv2_imread_mock) as imread_mock:
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                with patch('cv2.rectangle', return_value=True):
                    with patch('cv2.imencode', return_value=(True, Mock(tobytes=lambda: b'jpeg-data'))):
                        with patch('cv2.resize', return_value=build_image_mock(shape=(640, 640))) as resize_mock:
                            result = RecognitionController.query(database, build_image_mock(), [(1, 2, 3, 4)], returns_picture=True)
                            assert len(result.recognitions) == 1
                            assert result.picture == 'data:image/jpeg;base64,anBlZy1kYXRh' # encoded version of 'jpeg-data'
                            resize_mock.assert_called_once()

def test_query_and_return_image_with_known_identity(database: Session, identity: Identity):
    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=build_identify_mock(list(1.0 for i in range(0, 128)), identity, 0.8)):
        with patch('cv2.imread', side_effect=cv2_imread_mock):
            with patch('cv2.imwrite', side_effect=cv2_imwrite_mock):
                with patch('cv2.rectangle', return_value=True):
                    with patch('cv2.putText', return_value=True) as puttext_mock:
                        with patch('cv2.imencode', return_value=(True, Mock(tobytes=lambda: b'jpeg-data'))):
                            with patch('cv2.resize', return_value=build_image_mock(shape=(640, 640))) as resize_mock:
                                result = RecognitionController.query(database, build_image_mock(), [(1, 2, 3, 4)], returns_picture=True)
                                assert len(result.recognitions) == 1
                                assert result.picture == 'data:image/jpeg;base64,anBlZy1kYXRh' # encoded version of 'jpeg-data'
                                puttext_mock.assert_called()
                                resize_mock.assert_called_once()

def test_get_queries_without_result(database: Session):
    result = RecognitionController.get_queries(database)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_queries(database: Session, query: Query):
    result = RecognitionController.get_queries(database)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Query)
    assert result[0].id is not None

def test_get_query_not_found(database: Session):
    with pytest.raises(NoResultFound):
        RecognitionController.get_query(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_query(database: Session, query: Query):
    result = RecognitionController.get_query(database, query.id)
    assert isinstance(result, Query)
    assert result.id == query.id

def test_get_suggestions_without_result(database: Session):
    result = RecognitionController.get_suggestions(database)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_suggestions(database: Session, query: Query, identity: Identity):
    suggestion_1 = insert_suggestion(database, query)
    suggestion_2 = insert_suggestion(database, query, identity, score=0.5)
    result = RecognitionController.get_suggestions(database)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Suggestion)
    assert result[0].id == suggestion_1.id
    assert result[0].identity_id is None
    assert result[0].score is None
    assert result[1].id == suggestion_2.id
    assert result[1].identity_id == identity.id
    assert result[1].score == 0.5

def test_get_suggestion_not_found(database: Session, query: Query):
    suggestion = insert_suggestion(database, query)

    with pytest.raises(NoResultFound):
        RecognitionController.get_suggestion(database, query.id, UUID('00000000-0000-0000-0000-000000000000'))

    with pytest.raises(NoResultFound):
        RecognitionController.get_suggestion(database, UUID('00000000-0000-0000-0000-000000000000'), suggestion.id)

def test_get_suggestion(database: Session, query: Query):
    suggestion = insert_suggestion(database, query)
    result = RecognitionController.get_suggestion(database, query.id, suggestion.id)
    assert isinstance(result, Suggestion)
    assert result.id == suggestion.id
    assert result.query_id == query.id

def test_confirm_suggestion(database: Session, query: Query):
    identity_1 = insert_identity(database, first_name='Identity 1')
    identity_2 = insert_identity(database, first_name='Identity 2')

    suggestion_1 = insert_suggestion(database, query, identity_2, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)))
    suggestion_2 = insert_suggestion(database, query, identity_2, vec_low=list(2.0 for i in range(0, 64)), vec_high=list(2.0 + 32 for i in range(0, 64)))
    suggestion_3 = insert_suggestion(database, query, vec_low=list(3.0 for i in range(0, 64)), vec_high=list(3.0 + 32 for i in range(0, 64)))
    suggestion_4 = insert_suggestion(database, query, vec_low=list(4.0 for i in range(0, 64)), vec_high=list(4.0 + 32 for i in range(0, 64)))
    suggestion_5 = insert_suggestion(database, query, vec_low=list(5.0 for i in range(0, 64)), vec_high=list(5.0 + 32 for i in range(0, 64)))

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    for suggestion in [suggestion_1, suggestion_2, suggestion_3, suggestion_4]:
        (query_dir / f'{suggestion.id}.png').open('wb').close()

    with patch('cv2.imread', return_value=build_image_mock()) as imread:
        with patch('cv2.imwrite', Mock()) as imwrite:
            # Confirm first suggestion
            result = RecognitionController.confirm_suggestion(database, query.id, suggestion_1.id)
            assert result.id is not None
            assert result.identity_id == identity_2.id
            assert result.vec_low == list(1.0 for i in range(0, 64))
            assert result.vec_high == list(1.0 + 32 for i in range(0, 64))
            imread.assert_called_with(str(query_dir / f'{suggestion_1.id}.png'))
            imwrite.assert_called_with(str(FACES_DIR / str(identity_2.id) / f'{result.id}.png'), ['face-data'])
            imread.reset_mock()
            imwrite.reset_mock()

            # Confirm second suggestion
            result = RecognitionController.confirm_suggestion(database, query.id, suggestion_2.id, identity_1)
            assert result.id is not None
            assert result.identity_id == identity_1.id
            assert result.vec_low == list(2.0 for i in range(0, 64))
            assert result.vec_high == list(2.0 + 32 for i in range(0, 64))
            imread.assert_called_with(str(query_dir / f'{suggestion_2.id}.png'))
            imwrite.assert_called_with(str(FACES_DIR / str(identity_1.id) / f'{result.id}.png'), ['face-data'])
            imread.reset_mock()
            imwrite.reset_mock()

            # Confirm third suggestion
            result = RecognitionController.confirm_suggestion(database, query.id, suggestion_3.id, identity_1)
            assert result.id is not None
            assert result.identity_id == identity_1.id
            assert result.vec_low == list(3.0 for i in range(0, 64))
            assert result.vec_high == list(3.0 + 32 for i in range(0, 64))
            imread.assert_called_with(str(query_dir / f'{suggestion_3.id}.png'))
            imwrite.assert_called_with(str(FACES_DIR / str(identity_1.id) / f'{result.id}.png'), ['face-data'])
            imread.reset_mock()
            imwrite.reset_mock()

            # Confirm forth suggestion
            with pytest.raises(RecognitionException) as ei:
                RecognitionController.confirm_suggestion(database, query.id, suggestion_4.id)
            assert ei.value.args[0] == 'No identity provided'

            # Confirm fifth suggestion
            with pytest.raises(RecognitionException) as ei:
                RecognitionController.confirm_suggestion(database, query.id, suggestion_5.id, identity_1)
            assert ei.value.args[0] == 'Face file not found'

def test_delete_suggestion(database: Session, query: Query):
    suggestion_1 = insert_suggestion(database, query)
    suggestion_2 = insert_suggestion(database, query)

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    (query_dir / 'full.png').open('wb').close()
    (query_dir / f'{suggestion_1.id}.png').open('wb').close()
    (query_dir / f'{suggestion_2.id}.png').open('wb').close()

    assert (query_dir / 'full.png').exists()
    assert (query_dir / f'{suggestion_1.id}.png').exists()
    assert (query_dir / f'{suggestion_2.id}.png').exists()

    # Delete first suggestion
    RecognitionController.delete_suggestion(database, query.id, suggestion_1.id)
    with pytest.raises(NoResultFound):
        RecognitionController.get_suggestion(database, query.id, suggestion_1.id)
    assert (query_dir / 'full.png').exists()
    assert not (query_dir / f'{suggestion_1.id}.png').exists()
    assert (query_dir / f'{suggestion_2.id}.png').exists()

    # Delete second suggestion
    RecognitionController.delete_suggestion(database, query.id, suggestion_2.id)
    with pytest.raises(NoResultFound):
        RecognitionController.get_suggestion(database, query.id, suggestion_2.id)
    with pytest.raises(NoResultFound):
        RecognitionController.get_query(database, query.id)
    assert not query_dir.exists()

def test_clear_suggestions(database: Session, query: Query):
    suggestion_1 = insert_suggestion(database, query, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)))
    suggestion_2 = insert_suggestion(database, query, vec_low=list(2.0 for i in range(0, 64)), vec_high=list(2.0 + 32 for i in range(0, 64)))
    suggestion_3 = insert_suggestion(database, query, vec_low=list(3.0 for i in range(0, 64)), vec_high=list(3.0 + 32 for i in range(0, 64)))
    suggestion_4 = insert_suggestion(database, query, vec_low=list(4.0 for i in range(0, 64)), vec_high=list(4.0 + 32 for i in range(0, 64)))

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    for suggestion in [suggestion_1, suggestion_2, suggestion_3, suggestion_4]:
        (query_dir / f'{suggestion.id}.png').open('wb').close()

    RecognitionController.clear_suggestions(database)

    assert not query_dir.exists()
    assert len(RecognitionController.get_suggestions(database)) == 0

def test_compute_suggestions_with_high_confidence(database: Session, query: Query, identity: Identity):
    insert_face_encoding(database, identity, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)))

    suggestion_1 = insert_suggestion(database, query, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)), rect=[1, 1, 1, 1])
    suggestion_2 = insert_suggestion(database, query, vec_low=list(2.0 for i in range(0, 64)), vec_high=list(2.0 + 32 for i in range(0, 64)), rect=[2, 2, 2, 2])

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    (query_dir / 'full.png').open('wb').close()

    for suggestion in [suggestion_1, suggestion_2]:
        (query_dir / f'{suggestion.id}.png').open('wb').close()

    def identify_mock(database: Session, image, rect):
        result = {
            'identity': None,
            'score': None,
            'rect': {
                'start': {
                    'x': rect[3],
                    'y': rect[0],
                },
                'end': {
                    'x': rect[1],
                    'y': rect[2],
                }
            }
        }
        encoding = suggestion_2.vec_low + suggestion_2.vec_high

        if rect == [1, 1, 1, 1]:
            result['identity'] = identity
            result['score'] = 1.0
            encoding = suggestion_1.vec_low + suggestion_1.vec_high

        return Recognition(**result), encoding

    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=identify_mock):
        with patch('cv2.imread', return_value=Mock(__getitem__=lambda self, key: ['face-data'], shape=(800, 600))) as imread:
            with patch('cv2.imwrite', Mock()) as imwrite:
                RecognitionController.compute_suggestions(database)

    suggestions = RecognitionController.get_suggestions(database)
    assert len(suggestions) == 1
    assert suggestions[0].id == suggestion_2.id
    assert suggestions[0].identity_id is None
    assert suggestions[0].score is None

def test_compute_suggestions_with_low_confidence(database: Session, query: Query, identity: Identity):
    insert_face_encoding(database, identity, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)))

    suggestion_1 = insert_suggestion(database, query, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)), rect=[1, 1, 1, 1])
    suggestion_2 = insert_suggestion(database, query, vec_low=list(2.0 for i in range(0, 64)), vec_high=list(2.0 + 32 for i in range(0, 64)), rect=[2, 2, 2, 2])

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    (query_dir / 'full.png').open('wb').close()

    for suggestion in [suggestion_1, suggestion_2]:
        (query_dir / f'{suggestion.id}.png').open('wb').close()

    def identify_mock(database: Session, image, rect):
        result = {
            'identity': None,
            'score': None,
            'rect': {
                'start': {
                    'x': rect[3],
                    'y': rect[0],
                },
                'end': {
                    'x': rect[1],
                    'y': rect[2],
                }
            }
        }
        encoding = suggestion_2.vec_low + suggestion_2.vec_high

        if rect == [1, 1, 1, 1]:
            result['identity'] = identity
            result['score'] = 0.5
            encoding = suggestion_1.vec_low + suggestion_1.vec_high

        return Recognition(**result), encoding

    with patch('app.controllers.recognition.RecognitionController.identify', side_effect=identify_mock):
        with patch('cv2.imread', return_value=Mock(__getitem__=lambda self, key: ['face-data'], shape=(800, 600))) as imread:
            with patch('cv2.imwrite', Mock()) as imwrite:
                RecognitionController.compute_suggestions(database)

    suggestions = RecognitionController.get_suggestions(database)
    assert len(suggestions) == 2
    assert suggestions[0].id == suggestion_2.id
    assert suggestions[0].identity_id is None
    assert suggestions[0].score is None
    assert suggestions[1].id == suggestion_1.id
    assert suggestions[1].identity_id == identity.id
    assert suggestions[1].score == 0.5

def test_compute_suggestions_with_missing_file(database: Session, query: Query):
    suggestion = insert_suggestion(database, query, vec_low=list(1.0 for i in range(0, 64)), vec_high=list(1.0 + 32 for i in range(0, 64)), rect=[1, 1, 1, 1])

    query_dir = QUERIES_DIR / str(query.id)
    query_dir.mkdir(parents=True)

    RecognitionController.compute_suggestions(database)

    suggestions = RecognitionController.get_suggestions(database)
    assert len(suggestions) == 1
    assert suggestions[0].id == suggestion.id
    assert suggestions[0].identity_id is None
    assert suggestions[0].score is None

def test_identify_with_exceptions():
    with patch('face_recognition.face_encodings', return_value=[]):
        with pytest.raises(NoEncodingFoundException):
            RecognitionController.identify(database, None, None)

    with patch('face_recognition.face_encodings', return_value=[None, None]):
        with pytest.raises(MultipleEncodingFoundException):
            RecognitionController.identify(database, None, None)

def test_identity_with_unknown_identity(database: Session):
    with patch('face_recognition.face_encodings', return_value=[list(str(i) for i in range(0, 128))]):
        recognition, encoding = RecognitionController.identify(database, None, [10, 50, 60, 20])
        assert isinstance(recognition, Recognition)
        assert recognition.identity is None
        assert recognition.score is None
        assert recognition.rect.start.x == 20
        assert recognition.rect.start.y == 10
        assert recognition.rect.end.x == 50
        assert recognition.rect.end.y == 60
        assert encoding == list(float(i) for i in range(0, 128))

def test_identity_with_known_identity(database: Session, identity: Identity):
    insert_face_encoding(
        database,
        identity,
        vec_low=list(float(i) for i in range(0, 64)),
        vec_high=list(float(i + 64) for i in range(0, 64))
    )
    with patch('face_recognition.face_encodings', return_value=[list(str(i) for i in range(0, 128))]):
        recognition, encoding = RecognitionController.identify(database, None, [10, 50, 60, 20])
        assert isinstance(recognition, Recognition)
        assert recognition.identity is not None
        assert recognition.identity.id == identity.id
        assert recognition.score == 1.0
        assert recognition.rect.start.x == 20
        assert recognition.rect.start.y == 10
        assert recognition.rect.end.x == 50
        assert recognition.rect.end.y == 60
        assert encoding == list(float(i) for i in range(0, 128))
