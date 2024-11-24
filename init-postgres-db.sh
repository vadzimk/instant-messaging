#!/bin/bash

set -eu; # if varibales unset raise error, if error terminate
export PGPASSWORD="$POSTGRES_PASSWORD";

# Create database if not exists
if psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$DATABASE_NAME";
then
    echo "${DATABASE_NAME} already exists. Skipping...";
else
    if createdb -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -T template0 "$DATABASE_NAME"; then
        echo "${DATABASE_NAME} created";
        if ! ./restore.sh "$DATABASE_NAME"; then
            echo "Error restoring database" >&2;
            exit 1;
        fi;
    else
        echo "Error creating database" >&2;
        exit 1;
    fi;
fi;

# Create user if it doesn't exist
USER_EXISTS=$(psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -tc \
"SELECT 1 FROM pg_roles WHERE rolname = '$TARGET_USER';" | xargs)
if [ "$USER_EXISTS" != '1' ]; then
    if psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -c \
    "CREATE USER \"$TARGET_USER\" WITH PASSWORD '$TARGET_USER_PASSWORD';"; then
        echo "User ${TARGET_USER} created";
    else
        echo "Error creating user $TARGET_USER" >&2;
        exit 1;
    fi;
else
    echo "User ${TARGET_USER} already exists. Skipping..."
fi;

# Grant user privileges to the database
if ! psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -c \
"GRANT ALL PRIVILEGES ON DATABASE \"$DATABASE_NAME\" TO \"$TARGET_USER\";"; then
    echo "Error granting privileges to ${TARGET_USER}" >&2;
    exit 1;
else
    echo "Granted priviliges to user ${TARGET_USER}"
fi;
