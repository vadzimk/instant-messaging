#!/bin/bash

# This script creates:
# a PostgreSQL database and tries to restore it from the backup,
# a user, grants privileges,
# and modifies pg_hba.conf to allow remote access.
# Because it is responsible for restoring db on a separate container, it cannot reload configuration
#
# ----- Client code must run: -------
# docker exec -u postgres postgres pg_ctl reload
# -----------------------------------

#
# REQUIRED ENVIRONMENT VARIABLES:
#   POSTGRES_PASSWORD      - Password for the PostgreSQL superuser (e.g., postgres).
#   DATABASE_HOST          - Host where the PostgreSQL database is running.
#   DATABASE_PORT          - Port on which PostgreSQL is accepting connections.
#   POSTGRES_USER          - PostgreSQL superuser username (e.g., postgres).
#   DATABASE_NAME          - Name of the database to be created or used.
#   TARGET_USER            - The username of the new user.
#   TARGET_USER_PASSWORD   - The password for the new user.
#   ALLOWED_IP             - The IP address from which the user is allowed to connect.
#
# This script assumes you have psql, createdb, and restore.sh available.


set -eu; # if varibales unset raise error, if error terminate
export PGPASSWORD="$POSTGRES_PASSWORD";

# Create database if not exists
echo "Creating database: ${DATABASE_NAME}"
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
echo "Creating user: ${TARGET_USER}"
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
echo "Granting privileges to user: ${TARGET_USER} for database: ${DATABASE_NAME} "
if ! psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -c \
"GRANT ALL PRIVILEGES ON DATABASE \"$DATABASE_NAME\" TO \"$TARGET_USER\";"; then
    echo "Error granting privileges to ${TARGET_USER}" >&2;
    exit 1;
else
    echo "Granted priviliges to user ${TARGET_USER}"
fi;

