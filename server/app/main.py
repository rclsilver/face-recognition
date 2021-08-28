import os

from app import VERSION
from app.routers import identities, recognition
from fastapi import FastAPI

production = os.getenv('APP_ENV', 'production') == 'production'
debug_mode = os.getenv('APP_DEBUG', False)

app = FastAPI(
    title='Faces recognition',
    version=VERSION,
    debug=debug_mode,
)

# Create the routes
app.include_router(identities.router, prefix='/identities')
app.include_router(recognition.router, prefix='/recognition')
