#!/bin/bash

# This script:
# Forcefully drops a PostgreSQL database.
# Drops the associated user.
#
# REQUIRED ENVIRONMENT VARIABLES:
#   POSTGRES_PASSWORD      - Password for the PostgreSQL superuser (e.g., postgres).
#   DATABASE_HOST          - Host where the PostgreSQL database is running.
#   DATABASE_PORT          - Port on which PostgreSQL is accepting connections.
#   POSTGRES_USER          - PostgreSQL superuser username (e.g., postgres).
#   DATABASE_NAME          - Name of the database to be dropped.
#   TARGET_USER            - The username of the user to be dropped.
#
# This script assumes you have psql available.

set -eu; # if variables unset raise error, if error terminate
export PGPASSWORD="$POSTGRES_PASSWORD";

# Force drop the database
echo "Forcefully dropping database: ${DATABASE_NAME}"
psql_output=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -lqt)
DB_EXISTS=$(echo "$psql_output" | cut -d '|' -f 1 | grep -qw "$DATABASE_NAME"; echo $?)
if [ "$DB_EXISTS" -eq 0 ]; then
    if psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -c \
    "DROP DATABASE IF EXISTS \"$DATABASE_NAME\" WITH (FORCE);"; then
        echo "Database ${DATABASE_NAME} dropped";
    else
        echo "Error dropping database $DATABASE_NAME" >&2;
        exit 1;
    fi;
else
    echo "Database ${DATABASE_NAME} does not exist. Skipping..."
fi;

# Drop the user
echo "Dropping user: ${TARGET_USER}"
USER_EXISTS=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -tc \
"SELECT 1 FROM pg_roles WHERE rolname = '$TARGET_USER';" | xargs)
if [ "$USER_EXISTS" == '1' ]; then
    if psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -c \
    "DROP USER \"$TARGET_USER\";"; then
        echo "User ${TARGET_USER} dropped";
    else
        echo "Error dropping user $TARGET_USER" >&2;
        exit 1;
    fi;
else
    echo "User ${TARGET_USER} does not exist. Skipping..."
fi;
