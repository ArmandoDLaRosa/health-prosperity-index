import mysql.connector
import json
import os

def load_config(env):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        return config[env]

def initialize_database(env):
    db_config = load_config(env)

    db = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],  
        password=db_config['password'] 
    )
    cursor = db.cursor()

    cursor.execute(f"CREATE USER IF NOT EXISTS '{db_config['user']}'@'%' IDENTIFIED BY '{db_config['password']}'")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    cursor.execute(f"GRANT ALL PRIVILEGES ON {db_config['database']}.* TO '{db_config['user']}'@'%'")
    cursor.execute("FLUSH PRIVILEGES")

    cursor.execute(f"USE {db_config['database']}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS index_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATETIME,
        index_value FLOAT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cron_job_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        run_time DATETIME,
        status VARCHAR(255),
        message TEXT
    )
    """)

    db.commit()
    cursor.close()
    db.close()

if __name__ == "__main__":
    environment = os.getenv('ENVIRONMENT', 'development')
    initialize_database(env=environment)
