import json
import mysql.connector
import requests
from datetime import datetime
import os

ENV = os.getenv('ENVIRONMENT', 'development')

WEIGHTS = {
    "Population": 0.2,
    "Household Income": 0.3,
    "Number Of Finishers": 0.2,
    "Number Covered": 0.2,
    "Household Ownership": 0.1
}

API_URL = (
    "https://datausa.io/api/data?measures="
    "Population,"
    "Household Income,"
    "Number Of Finishers,"
    "Number Covered,"
    "Household Ownership"
)

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0

def impute_missing_values(item, historical_data, key):
    if key in item:
        return item[key]
    else:
        return sum(hist_item.get(key, 0) for hist_item in historical_data) / len(historical_data)

def calculate_index(data, historical_data):
    all_data = data + historical_data
    
    indices = []
    min_values = {key: min(item.get(key, 0) for item in all_data) for key in WEIGHTS}
    max_values = {key: max(item.get(key, 0) for item in all_data) for key in WEIGHTS}

    for item in data:
        normalized_values = {}
        for key in WEIGHTS:
            value = impute_missing_values(item, all_data, key)
            normalized_values[key] = normalize(value, min_values[key], max_values[key])
        
        index_value = sum(normalized_values[key] * WEIGHTS[key] for key in WEIGHTS)
        indices.append({
            "year": int(item["Year"]),
            "index_value": index_value,
            "components": item  
        })
    return indices


def load_config():
    source = '/usr/src/app/config/config.json' if ENV == 'production' else '/home/armando/repos/health-prosperity-index/config/config.json'
    with open(source, 'r') as config_file:
        config = json.load(config_file)
        return config[ENV]

def log_cron_status(status, message):
    db_config = load_config()
    cursor = None 
    
    try:
        db = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = db.cursor() 
        cursor.execute("""
            INSERT INTO cron_job_logs (run_time, status, message)
            VALUES (%s, %s, %s);
        """, (datetime.now(), status, message))
        db.commit()

    except mysql.connector.Error as err:
        print("Failed to log into database")
    finally:
        if cursor is not None:
            cursor.close() 
        db.close()


def update_index_in_db(index_data):
    db_config = load_config()

    try:
        db = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = db.cursor()

        for index in index_data:
            cursor.execute("""
                INSERT INTO index_table (year, index_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE index_value = VALUES(index_value), updated_at = CURRENT_TIMESTAMP;
            """, (index["year"], index["index_value"]))

            cursor.execute("""
                INSERT INTO index_components (year, population, household_income, number_of_finishers, number_covered, household_ownership)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    population = VALUES(population), 
                    household_income = VALUES(household_income),
                    number_of_finishers = VALUES(number_of_finishers),
                    number_covered = VALUES(number_covered),
                    household_ownership = VALUES(household_ownership),
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                index["year"],
                index["components"].get("Population"),
                index["components"].get("Household Income"),
                index["components"].get("Number Of Finishers"),
                index["components"].get("Number Covered"),
                index["components"].get("Household Ownership")
            ))

        db.commit()

    except mysql.connector.Error as err:
        log_cron_status('FAILURE', f"Database error: {err}")
        raise 
    finally:
        cursor.close()
        db.close()

def fetch_api_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  
        return response.json()["data"]
    except requests.exceptions.RequestException as err:
        log_cron_status('FAILURE', f"API request error: {err}")
        raise 

def fetch_api_years(api_data):
    return {int(item['Year']) for item in api_data}

def fetch_missing_years_from_db(api_years):
    db_config = load_config()
    
    try:
        db = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = db.cursor(dictionary=True)
        format_strings = ','.join(['%s'] * len(api_years))
        cursor.execute(f"SELECT * FROM index_components WHERE year NOT IN ({format_strings});", tuple(api_years))
        missing_years_data = cursor.fetchall()
        return missing_years_data

    except mysql.connector.Error as err:
        log_cron_status('FAILURE', f"Database error when fetching missing years: {err}")
        raise
    finally:
        cursor.close()
        db.close()

def main():
    try:
        data = fetch_api_data()
        
        if data:
            api_years = fetch_api_years(data)            
            missing_years_data = fetch_missing_years_from_db(api_years)                        
            index_data = calculate_index(data, missing_years_data)
            update_index_in_db(index_data)
            log_cron_status('SUCCESS', 'Index calculation and database update completed successfully.')
        else:
            log_cron_status('SUCCESS', 'No new data to process. API returned no data.')
    except Exception as e:
        log_cron_status('FAILURE', f"Critical error: {e}")

if __name__ == "__main__":
    main()
