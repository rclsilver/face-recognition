import logging

from app.database import get_session
from app.schemas.users import User
from fastapi import Depends, HTTPException, Request, status
from ipaddress import IPv4Address, IPv4Network
from sqlalchemy.orm import Session
from typing import List


_auth_instance = None


class AuthException(Exception):
    """
    Base authentication exception
    """
    pass


class AuthConfigureException(AuthException):
    """
    Auth configuration exception
    """
    pass


class BaseAuth:
    """
    Base auth class
    """
    
    def __init__(self, source_whitelist: List[str]):
        """
        Initialize the class
        """
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._source_whitelist = source_whitelist

    def is_whitelist(self, client_ip: str) -> bool:
        """
        Is the client IP in the whitelist
        """
        ip = IPv4Address(client_ip)

        for network in (IPv4Network(net) for net in self._source_whitelist):
            if ip in network:
                return True
        return False

    def get_user_with_token(self, token: str, db: Session) -> User:
        """
        Get or create user from token string
        """
        raise NotImplementedError()

    def get_user(self, request: Request, db: Session) -> User:
        """
        Get or create user from authorization header
        """
        raise NotImplementedError()

    def raise_auth_exception(self, headers={}) -> None:
        """
        Raise HTTPException
        """
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers=headers,
        )


def configure_auth(auth_cls, *args, **kwargs):
    """
    Configure auth
    """
    global _auth_instance
    _auth_instance = auth_cls(*args, **kwargs)


def get_auth() -> BaseAuth:
    """
    Get current auth instance
    """
    global _auth_instance
    return _auth_instance


def get_user(
    request: Request,
    auth: BaseAuth = Depends(get_auth),
    db: Session = Depends(get_session)
) -> User:
    """
    Get or create user from the request
    """
    return auth.get_user(request, db)


def check_is_admin(user: User, raises: bool = True) -> bool:
    """
    Check if user is administrator and raise HTTPException if raises is True,
    otherwise, return bool
    """
    if user.is_admin:
        return True
    elif not raises:
        return False
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'You are not allowed to execute this action')
