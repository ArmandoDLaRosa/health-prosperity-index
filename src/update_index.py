import requests
import mysql.connector
import json
from datetime import datetime
import numpy as np
import smtplib
from email.mime.text import MIMEText

API_URL = "https://datausa.io/api/data?some-endpoint"

def load_config(env):
    with open('/usr/src/app/config/config.json', 'r') as config_file:
        config = json.load(config_file)
        return config[env]

def fetch_data_from_api():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log_error(f"API request failed: {e}")
        return None

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def calculate_index(data):
    life_expectancy = data.get("life_expectancy")
    median_income = data.get("median_income")
    education_level = data.get("education_level")
    unemployment_rate = data.get("unemployment_rate")

    life_expectancy_norm = normalize(life_expectancy, 50, 90)
    median_income_norm = normalize(median_income, 20000, 100000)
    education_level_norm = normalize(education_level, 0, 1)
    unemployment_rate_norm = normalize(unemployment_rate, 0, 10)

    index = (0.4 * life_expectancy_norm +
             0.3 * median_income_norm +
             0.2 * education_level_norm -
             0.1 * unemployment_rate_norm)
    
    return index

def update_index_in_db(index, env='production'):
    db_config = load_config(env)

    try:
        db = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = db.cursor()
        cursor.execute("INSERT INTO index_table (date, index_value) VALUES (%s, %s)",
                       (datetime.now(), index))
        db.commit()
        cursor.close()
        db.close()
    except mysql.connector.Error as e:
        log_error(f"Database update failed: {e}")

def log_error(message):
    with open("/var/log/app_errors.log", "a") as log_file:
        log_file.write(f"{datetime.now()} - ERROR - {message}\n")

def send_email_alert(subject, body):
    sender_email = "your-email@gmail.com"
    receiver_email = "recipient-email@gmail.com"
    password = "your-app-password"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        with open("/var/log/app_errors.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - ERROR - Failed to send email: {e}\n")

def main():
    data = fetch_data_from_api()
    if data:
        index = calculate_index(data)
        update_index_in_db(index)
    else:
        log_error("Failed to fetch data from API")
        send_email_alert("Cron Job Failure", "Failed to fetch data from API")

if __name__ == "__main__":
    main()
