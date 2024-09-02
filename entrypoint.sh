#!/bin/bash

# Ensure MariaDB data directory exists and is owned by the mysql user
mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld

# Start MariaDB service
echo "Starting MariaDB service..."
/usr/bin/mysqld_safe --datadir='/var/lib/mysql' &

# Wait for MariaDB to start
until mysqladmin ping -h "$MYSQL_HOST" --silent; do
    echo "Waiting for MariaDB to start..."
    sleep 2
done

# Check if the database exists
DB_EXISTS=$(mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "SHOW DATABASES LIKE '$MYSQL_DB';" | grep "$MYSQL_DB" > /dev/null; echo "$?")
if [ $DB_EXISTS -eq 1 ]; then
    echo "Database $MYSQL_DB does not exist. Initializing database..."
    python3 src/init_db.py
else
    echo "Database $MYSQL_DB already exists."
fi

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Set up cron job to run update_index.py every day at midnight
echo "Setting up cron job..."
(crontab -l ; echo "0 0 * * * python /usr/src/app/health-prosperity-index/src/update_index.py >> /var/log/cron.log 2>&1") | crontab -

# Start cron service
echo "Starting cron service..."
service cron start

# Run the main container process (Streamlit app)
exec "$@"
