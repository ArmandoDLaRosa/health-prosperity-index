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

DB_EXISTS=$(mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "SHOW DATABASES LIKE '$MYSQL_DB';" | grep "$MYSQL_DB" > /dev/null; echo "$?")
if [ $DB_EXISTS -eq 1 ]; then
    echo "Database $MYSQL_DB does not exist. Initializing database..."
    python3 /usr/src/app/health-prosperity-index/src/init_db.py
else
    echo "Database $MYSQL_DB already exists."
fi


echo "Setting up cron job..."
(crontab -l ; echo "0 0 * * * python /usr/src/app/health-prosperity-index/src/update_index.py >> /var/log/cron.log 2>&1") | crontab -

cd /usr/src/app/health-prosperity-index

echo "Applying database migrations..."
alembic upgrade head

echo "Starting cron service..."
service cron start

exec "$@"
