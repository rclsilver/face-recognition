import logging
import os

from app import get_app, get_cli


DEBUG = os.getenv('APP_DEBUG', 'false').lower() == 'true'


logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO
)

if __name__ == '__main__':
    # CLI mode
    cli = get_cli()
    cli()
else:
    # API mode
    app = get_app(
        os.getenv('OIDC_ISSUER'),
        os.getenv('APP_PREFIX', ''),
        os.getenv('APP_ENV', 'production').lower() == 'production',
        DEBUG,
        os.getenv('AUTH_WHITELIST', '').split(',')
    )
