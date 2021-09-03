import logging
import os

logging.basicConfig(
    level=logging.DEBUG
)

from app import VERSION
from app.routers import cameras, identities, recognition, users
from fastapi import FastAPI

production = os.getenv('APP_ENV', 'production') == 'production'
debug_mode = os.getenv('APP_DEBUG', 'false') == 'true'

app = FastAPI(
    title='Faces recognition',
    version=VERSION,
    debug=debug_mode,
    root_path=os.getenv('APP_PREFIX', ''),
)

# Create the routes
app.include_router(identities.router, prefix='/identities')
app.include_router(recognition.router, prefix='/recognition')
app.include_router(cameras.router, prefix='/cameras')
app.include_router(users.router, prefix='/users')
