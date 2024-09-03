import streamlit as st
import mysql.connector
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os 
ENV = os.getenv('ENVIRONMENT', 'development')

def load_config():
    source = '/usr/src/app/config/config.json' if ENV == 'production' else '/home/armando/repos/health-prosperity-index/config/config.json'
    with open(source, 'r') as config_file:
        config = json.load(config_file)
        return config[ENV]

def get_db_connection():
    db_config = load_config()
    return mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

def fetch_data(query):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return pd.DataFrame(result)

def main():
    st.title('US Health and Prosperity Index')

    index_data = fetch_data("SELECT * FROM index_table")
    st.subheader("Health and Prosperity Index Data")
    if not index_data.empty:
        st.table(index_data) 

        st.subheader("Health and Prosperity Index Over Time")
        fig = px.line(index_data, x='year', y='index_value', title='Index Value Over Years')
        st.plotly_chart(fig)

    cron_logs = fetch_data("SELECT * FROM cron_job_logs")
    st.subheader("Cron Job Logs")
    if not cron_logs.empty:
        st.table(cron_logs)  

    components_data = fetch_data("SELECT * FROM index_components")
    st.subheader("Index Components Data")
    if not components_data.empty:
        st.table(components_data)
        
        components_data['household_income'].fillna(0, inplace=True)

        st.subheader("Components Over Time")
        fig = px.scatter(
            components_data, 
            x='year', 
            y='population', 
            size='household_income',  
            color='number_of_finishers',
            title='Population vs Household Income Over Time',
            hover_data={'household_income': True, 'number_of_finishers': True, 'year': True},
            labels={
                'population': 'Population',
                'household_income': 'Household Income',
                'number_of_finishers': 'Number of Finishers',
                'year': 'Year'
            }
        )
        
        explanation_text = ("This scatter plot visualizes the relationship between Population and Household Income over the years.\n"
                            "The size of each marker represents the Household Income, and the color indicates the Number of Finishers.\n"
                            "Hover over each point to see detailed information about the year, population, household income, and number of finishers.")
        
        fig.add_annotation(
            text=explanation_text,
            xref="paper", yref="paper",
            x=0.5, y=1.15, showarrow=False,
            font=dict(size=12),
            align="center"
        )

        st.plotly_chart(fig)

    if not cron_logs.empty:
        st.subheader("Cron Job Execution Status")
        status_counts = cron_logs['status'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  
        st.pyplot(fig)

if __name__ == "__main__":
    main()