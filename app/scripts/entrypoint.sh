#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - running migrations"

# Run migrations
alembic upgrade head

>&2 echo "Migrations applied - starting server"

# Start the FastAPI server
exec uvicorn --workers 1 --host 0.0.0.0 --port $APPLICATION_SERVER_PORT app.main:app
