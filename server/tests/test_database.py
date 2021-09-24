from app.database import get_url, get_session
from collections import deque
from unittest.mock import patch
from sqlalchemy.orm.session import Session
from typing import Generator


def getenv_mock(key):
    return {
        'DB_USER': 'db-user',
        'DB_PASS': 'db-pass',
        'DB_HOST': 'db-host',
        'DB_NAME': 'db-name'
    }.get(key)

def test_get_url():
    with patch('os.getenv', side_effect=getenv_mock):
        result = get_url()
        assert result == 'postgresql://db-user:db-pass@db-host/db-name'

def test_get_session():
    result = get_session()
    assert isinstance(result, Generator)
    result = deque(result)
    assert len(result) == 1
    assert isinstance(result[0], Session)
