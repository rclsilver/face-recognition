#!/usr/bin/env bash

LISTEN_HOST=0.0.0.0
LISTEN_PORT=8000
APP_ENTRY_POINT=main:app

# Development mode
if [ "${APP_ENV:=production}" == "development" ]; then
    echo "[development] Running application in development mode"
    uvicorn \
        --host ${LISTEN_HOST} \
        --port ${LISTEN_PORT} \
        --reload \
        --log-level debug \
        ${APP_ENTRY_POINT}
else
    echo "[production] Running application in production mode"

    if [ $(id -u) -eq 0 ]; then
        # Change app user and group ID
        groupmod -o -g "${APP_GID:=1000}" app
        usermod -o -u "${APP_UID:=1000}" app

        USER_PARAMS="-u app -g app"
    fi

    # Use gunicorn to run the application
    gunicorn ${USER_PARAMS} \
        -w ${GUNICORN_WORKERS:-5} \
        -k uvicorn.workers.UvicornWorker \
        -b ${LISTEN_HOST}:${LISTEN_PORT} \
        ${APP_ENTRY_POINT}
fi
