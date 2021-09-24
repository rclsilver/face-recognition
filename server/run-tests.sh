#!/usr/bin/env bash

docker-compose -f docker-compose.tests.yml -p face_recognition_tests up --force-recreate --abort-on-container-exit
docker-compose -f docker-compose.tests.yml -p face_recognition_tests down
