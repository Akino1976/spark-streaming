#!/bin/bash
set -e
set -u
POSTGRES_DATABASES=(
    finance_data_landing_docker_eu
    finance_data_landing_docker_ap1
    finance_data_landing_docker_us
    finance_data_dcl_docker
)

function create_user_and_database() {
    local database=$1
    echo "  Creating user and database '$database'"
    psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '${database}'" | \
    grep -q 1 || \
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE ${database} ENCODING = 'UTF8' CONNECTION LIMIT = -1;"
}

if [ -n "$POSTGRES_DATABASES" ]; then
    echo "Create database: $POSTGRES_DATABASES"
    for database in "${POSTGRES_DATABASES[@]}"; do
        echo "###################################################"
        printf "# Creating database (%s) \n" "$database"
        echo "###################################################"
        create_user_and_database $database
    done
    echo "Multiple databases created"
fi
