def get_version():
    """
    Build current version
    """
    return '1.0.0'

def get_app(
    oidc_issuer: str,
    app_prefix: str = '',
    production: bool = True,
    debug: bool = True
):
    from app.auth import configure_auth
    from app.auth.oidc import OidcAuth
    from app.routers import cameras, identities, recognition, users
    from fastapi import FastAPI

    # Configure authentication
    configure_auth(OidcAuth, oidc_issuer)

    # Initialize the application
    app = FastAPI(
        title='Faces recognition',
        version=get_version(),
        debug=debug,
        production=production,
        root_path=app_prefix,
    )

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
