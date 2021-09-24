import logging
import re

from typing import List


def get_version():
    """
    Build current version
    """
    return '1.0.0'

def get_app(
    oidc_issuer: str,
    app_prefix: str = '',
    production: bool = True,
    debug: bool = True,
    source_whitelist: List[str] = []
):
    from app.auth import configure_auth
    from app.auth.oidc import OidcAuth
    from app.routers import cameras, identities, recognition, users
    from fastapi import FastAPI, Request, status

    # Configure authentication
    configure_auth(OidcAuth, oidc_issuer, source_whitelist)

    # Initialize the application
    app = FastAPI(
        title='Faces recognition',
        version=get_version(),
        debug=debug,
        production=production,
        root_path=app_prefix,
        source_whitelist=source_whitelist
    )

    if production:
        access_logger = logging.getLogger(__name__)
        re_status = re.compile('^HTTP_[0-9]+_(.+)$')
        status_strings = { 
            v: re_status.match(k).group(1).replace('_', ' ') for k, v in status.__dict__.items() if k.startswith('HTTP_')
        }

        @app.middleware('http')
        async def access_log(request: Request, call_next):
            response = await call_next(request)

            access_logger.info(
                '%s:%d - "%s %s %s" %d %s',
                request.client.host,
                request.client.port,
                request.method,
                request.url,
                'HTTP/{}'.format(request.scope['http_version']),
                response.status_code,
                status_strings.get(response.status_code, '')
            )
            access_logger.debug('Headers: %s', request.headers)

            return response

    # Create the routes
    app.include_router(identities.router, prefix='/identities')
    app.include_router(recognition.router, prefix='/recognition')
    app.include_router(cameras.router, prefix='/cameras')
    app.include_router(users.router, prefix='/users')

    return app


def get_cli():
    """
    Get CLI instance
    """
    from app.commands import cli

    return cli
