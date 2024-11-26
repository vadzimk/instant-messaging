#!/bin/bash

# This script modifies PostgreSQL's `pg_hba.conf` file
# to allow remote access to a specific database for a given user from a specified IP address.
#
# Environment Variables:
#   POSTGRES_USER: The PostgreSQL superuser used to run the script.
#   DATABASE_NAME: The name of the database to grant remote access.
#   TARGET_USER: The username for which remote access is being configured.
#   ALLOWED_IP: The IP address (in CIDR format) allowed to connect to the database.


# get the path of pb_hba.conf
HBA_FILE_PATH=$(psql -U $POSTGRES_USER -t -A -c "SHOW hba_file;")

# modify pb_hba.conf to allow remote access
if ! grep -q "host\s\+${DATABASE_NAME}\s\+${TARGET_USER}\s\+${ALLOWED_IP}/32" "$HBA_FILE_PATH"; then
  # If it doesn't exist, append the new record
  echo "host    ${DATABASE_NAME}    ${TARGET_USER}    ${ALLOWED_IP}/32    md5" >> "$HBA_FILE_PATH"
else
  echo "Record already exists in ${HBA_FILE_PATH} Skipping..."
fi