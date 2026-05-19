#!/bin/sh

set -e

if [ "$DEPLOY_ENV" = "dev" ]
then
    echo "Running Development Server"
    exec uvicorn main:app --host 0.0.0.0 --port 8080 --reload
elif [ "$DEPLOY_ENV" = "testing" ]
then
    echo "Running Testing Server"
    exec pytest
else
    echo "Running Production Server"
    exec uvicorn main:app --host 0.0.0.0 --port 8080 --log-level critical --no-access-log
fi

exec "$@"
