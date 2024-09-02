import streamlit as st
import mysql.connector
import json

def load_config(env):
    with open('/usr/src/app/config/config.json', 'r') as config_file:
        config = json.load(config_file)
        return config[env]

db_config = load_config(env='production') 

db = mysql.connector.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)

cursor = db.cursor()

st.title('US Health and Prosperity Index')

cursor.execute("SELECT * FROM index_table")
rows = cursor.fetchall()

st.write("Health and Prosperity Index Data")
st.table(rows)

cursor.execute("SELECT * FROM cron_job_logs")
logs = cursor.fetchall()

st.write("Cron Job Logs")
st.table(logs)

cursor.close()
db.close()
