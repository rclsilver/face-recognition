#!/usr/bin/env bash

LISTEN_HOST=0.0.0.0
LISTEN_PORT=8000
APP_ENTRY_POINT=main:app

case "${APP_ENV:=production}" in
    development)
        echo "[development] Running application in development mode"
        uvicorn \
            --host ${LISTEN_HOST} \
            --port ${LISTEN_PORT} \
            --reload \
            --log-level debug \
            ${APP_ENTRY_POINT}
        ;;
    
    production)
        echo "[production] Running application in production mode"

        # Change app user and group ID
        groupmod -o -g "${APP_GID:=1000}" app
        usermod -o -u "${APP_UID:=1000}" app

        if [ "${APP_TYPE:=server}" == "server" ]; then
            # Use gunicorn to run the application
            gunicorn \
                -u app -g app \
                -w ${GUNICORN_WORKERS:-5} \
                -k uvicorn.workers.UvicornWorker \
                -b ${LISTEN_HOST}:${LISTEN_PORT} \
                ${APP_ENTRY_POINT}
        elif [ "${APP_TYPE}" == "cameras" ]; then
            su app -c "python /usr/src/main.py cameras run"
        fi
        ;;

    tests)
        echo "[tests] Executing tests"
        pytest --cov=. --cov-report term --cov-report html tests/
        ;;

    *)
        echo "Invalid environment '${APP_ENV}'" >&2
        exit 1
esac
