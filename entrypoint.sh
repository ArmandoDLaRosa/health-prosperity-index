#!/bin/bash

echo "Current working directory: $(pwd)"

mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld

echo "Starting MariaDB service..."
/usr/bin/mysqld_safe --datadir='/var/lib/mysql' &

until mysqladmin ping -h "$MYSQL_HOST" --silent; do
    echo "Waiting for MariaDB to start..."
    sleep 2
done

DB_EXISTS=$(mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES LIKE '$MYSQL_DB';" | grep "$MYSQL_DB" > /dev/null; echo "$?")
if [ $DB_EXISTS -eq 1 ]; then
    echo "Database $MYSQL_DB does not exist. Initializing database..."
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DB;"
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '$MYSQL_USER'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';"
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON $MYSQL_DB.* TO '$MYSQL_USER'@'%';"
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"
    echo "Database $MYSQL_DB and user $MYSQL_USER initialized."
else
    echo "Database $MYSQL_DB already exists."
fi


echo "Setting up cron job..."

CRONTAB_EXISTS=$(crontab -l 2>/dev/null | grep -v "no crontab" | wc -l)

if [ $CRONTAB_EXISTS -eq 0 ]; then
    echo "No existing crontab found. Creating a new one."
    echo "*/5 * * * * ENVIRONMENT=production /usr/local/bin/python /usr/src/app/src/update_index.py >> /var/log/cron.log 2>&1" | crontab -
else
    echo "Appending to existing crontab."
    (crontab -l ; echo "*/5 * * * * ENVIRONMENT=production /usr/local/bin/python /usr/src/app/src/update_index.py >> /var/log/cron.log 2>&1") | crontab -
fi

cd /usr/src/app/

echo "Applying database migrations..."
alembic upgrade head

echo "Starting cron service..."
service cron start

exec "$@"

tail -f /var/log/cron.log
