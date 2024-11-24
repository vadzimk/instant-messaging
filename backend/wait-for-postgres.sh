#!/bin/sh

set -e

UNSET_VARS=""

# Check if required environment variables are set
[ -z "$POSTGRES_APP_USER" ] && UNSET_VARS="$UNSET_VARS POSTGRES_APP_USER"
[ -z "$POSTGRES_APP_PASSWORD" ] && UNSET_VARS="$UNSET_VARS POSTGRES_APP_PASSWORD"
[ -z "$POSTGRES_HOST" ] && UNSET_VARS="$UNSET_VARS POSTGRES_HOST"
[ -z "$POSTGRES_PORT" ] && UNSET_VARS="$UNSET_VARS POSTGRES_PORT"
[ -z "$POSTGRES_DB" ] && UNSET_VARS="$UNSET_VARS POSTGRES_DB"

# If any variables are unset, echo an error message and exit
if [ -n "$UNSET_VARS" ]; then
  echo "Error: The following required environment variables are not set:$UNSET_VARS"
  exit 1
fi

CONNECTION_STRING="postgres://${POSTGRES_APP_USER}:${POSTGRES_APP_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
#shift  # shifts the positional parameters to the left, effectively removing the first argument (the connection string)

until pg_isready -d "$CONNECTION_STRING"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

#exec "$@" # replaces the current shell with the command that was passed as arguments to the script (after the connection string). The command will now be executed in the same process, inheriting the environment and any changes made.

