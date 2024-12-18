#!/bin/bash
set -e
echo "Starting entrypoint script"
echo "Listing current directory contents:"
pwd
ls -htla

if [ -f "wait-for-postgres.sh" ]; then
  echo "Found wait-for-postgres.sh, sourcing it"
  . wait-for-postgres.sh
else
  echo "Error: wait-for-postgres.sh not found"
  echo "Debugging: Search for wait-for-postgres.sh in the filesystem"
  find / -name "wait-for-postgres.sh" 2>/dev/null
  exit 1
fi

echo "wait-for-postgres.sh script completed"

cd /usr/src/app || { echo "Failed to change to /usr/src/app directory"; exit 1; };

if [ ! -d migrations ]; then
  echo "Existing migrations directory not found, Initializing migrations...."
  alembic init -t async migrations || { echo "Failed to initialize migrations"; exit 1; };
  alembic revision --autogenerate -m "Initial migration" || { echo "Failed to create initial migration"; exit 1; }
fi;

alembic upgrade head || { echo "Migration upgrade failed"; exit 1; }
#exec celery -A app.celery worker --loglevel=info --concurrency=1 &
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers=1 || { echo "Failed to start the application"; exit Ï1; };