#!/bin/bash

mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld

echo "Starting MySQL service..."
service mysql start

until mysqladmin ping -h "$MYSQL_HOST" --silent; do
    echo "Waiting for MySQL to start..."
    sleep 2
done

DB_EXISTS=$(mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW DATABASES LIKE '$MYSQL_DB';" | grep "$MYSQL_DB" > /dev/null; echo "$?")
if [ $DB_EXISTS -eq 1 ]; then
    echo "Database $MYSQL_DB does not exist. Initializing database..."
    python /usr/src/app/init_db.py
fi

echo "Applying database migrations..."
alembic upgrade head

exec "$@"
