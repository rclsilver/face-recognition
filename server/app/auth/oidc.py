import base64
import jwt
import requests

from app.auth import AuthConfigureException, BaseAuth
from app.controllers.users import UserController
from app.database import get_session
from app.schemas.users import User
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from fastapi import HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from typing import Dict, List, Optional


class OidcAuth(BaseAuth):
    """
    OpenID Connect auth
    """
    def __init__(self, issuer_url: str, source_whitelist: List[str]):
        """
        Initialize OIDC auth with the issuer URL
        """
        super().__init__(source_whitelist)

        self._issuer_url = issuer_url
        self._configuration = self._load_configuration()
        self._certificates = self._load_certificates()

    def _load_configuration(self) -> Dict:
        """
        Returns OpenID configuration from issuer
        """
        configuration_url = f'{self._issuer_url}/.well-known/openid-configuration'
        try:
            res = requests.get(configuration_url)
            res.raise_for_status()
            self._logger.debug(f'OpenID configuration loaded from {configuration_url} successfully')
            return res.json()
        except Exception as e:
            self._logger.exception(f'Error while loading openid configuration from {configuration_url}')
            raise AuthConfigureException(e)

    def _load_x509_der_certificate(self, key: Dict) -> x509.Certificate:
        """
        Parse and load x509 DER certificate
        """
        self._logger.debug('Loading key %s (alg: %s, type: %s)', key['kid'], key['alg'], key['kty'])
        certificate_bytes = base64.b64decode(key['x5c'][0].encode('ascii'))
        certificate = x509.load_der_x509_certificate(certificate_bytes, default_backend())
        self._logger.debug('Key %s successfully loaded', key['kid'])
        return certificate

    def _load_certificates(self) -> Dict:
        """
        Download auth server certificates
        """
        try:
            certificates_url = self._configuration['jwks_uri']
            res = requests.get(certificates_url)
            res.raise_for_status()
            self._logger.debug(f'OpenID certificates downloaded from {certificates_url} successfully')
            return {
                key['kid']: {
                    'x509': self._load_x509_der_certificate(key),
                    'alg': key['alg']
                } for key in res.json()['keys']
            }
        except Exception as e:
            self._logger.exception(f'Error while loading openid certificates from {certificates_url}')
            raise AuthConfigureException(e)

    def raise_auth_exception(self) -> None:
        """
        Raise HTTPException
        """
        super().raise_auth_exception({
            'WWW-Authenticate': 'Bearer'
        })

    def _decode_token(self, token: str) -> Dict:
        """
        Decode a JWT token and return its payload
        """
        token_header = jwt.get_unverified_header(token)
        token_kid = token_header.get('kid')

        if not token_kid in self._certificates:
            self.raise_auth_exception()

        token_key_certificate = self._certificates.get(token_kid)

        try:
            return jwt.decode(
                token,
                key=token_key_certificate['x509'].public_key(),
                algorithms=[token_key_certificate['alg']],
                audience='account'
            )
        except Exception:
            self._logger.debug('Unable to decode JWT token', exc_info=True)
            self.raise_auth_exception()

    def get_user_with_token(self, token: str, db: Session) -> User:
        """
        Get or create user from token string
        """
        token_payload = self._decode_token(token)

        return UserController.get_or_create_user(
            db,
            token_payload.get('preferred_username'),
            '/administrateurs' in token_payload.get('groups', [])
        )

    def get_user(self, request: Request, db: Session) -> Optional[User]:
        """
        Get or create user from authorization header
        """
        if self.is_whitelist(request.client.host):
            self._logger.debug('Client %s is in the whitelist', request.client.host)
            return UserController.get_or_create_user(db, 'internal', True)

        scheme, token = get_authorization_scheme_param(request.headers.get('authorization'))

        if scheme.lower() != 'bearer':
            self.raise_auth_exception()

        return self.get_user_with_token(token, db)
