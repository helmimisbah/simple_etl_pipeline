from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime, timedelta
import requests
import json
import os

POSTGRES_CONN_ID='postgres_default'
API_CONN_ID='openweather_api'
API_KEY = 'YOUR_API_KEY'  # Replace with your actual OpenWeather API key
LATITUDE='-6.200'   # I'm using Jakarta's coordinate
LONGITUDE='106.8166'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 20),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_to_postgres_hook',
    default_args=default_args,
    description='Fetch real-time weather data for Jakarta and store it directly into PostgreSQL using PostgresHook',
    schedule_interval='@hourly',
    catchup=False,
)

def extract_data(**kwargs):
    http_hook=HttpHook(http_conn_id=API_CONN_ID,method='GET')
    endpoint = f"/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"
    
    response=http_hook.run(endpoint)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")

def transform_data(**kwargs):
    ti = kwargs['ti']
    raw_data = ti.xcom_pull(task_ids='extract_data')
    
    processed_data = {
        "city": raw_data.get("name"),
        "temperature": raw_data.get("main", {}).get("temp"),
        "humidity": raw_data.get("main", {}).get("humidity"),
        "weather_description": raw_data.get("weather", [{}])[0].get("description"),
        "timestamp": raw_data.get("dt")
    }
    return processed_data

def load_data(**kwargs):
    ti = kwargs['ti']
    processed_data = ti.xcom_pull(task_ids='transform_data')  
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        city VARCHAR(50),
        temperature FLOAT,
        humidity INT,
        weather_description VARCHAR(100),
        timestamp BIGINT
    );
    """
    pg_hook.run(create_table_query)

    insert_query = """
    INSERT INTO weather_data (city, temperature, humidity, weather_description, timestamp)
    VALUES (%s, %s, %s, %s, %s);
    """
    parameters = (
        processed_data["city"],
        processed_data["temperature"],
        processed_data["humidity"],
        processed_data["weather_description"],
        processed_data["timestamp"],
    )
    pg_hook.run(insert_query, parameters=parameters)

# Define tasks
extract_data_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

extract_data_task >> transform_data_task >> load_data_task
