# ETL Weather Data Pipeline

A real-time data pipeline that uses Apache Airflow to fetch weather data from the OpenWeather API for Jakarta and store it directly into a PostgreSQL database using Airflow’s HttpHook and PostgresHook.

## Overview

This project monitors real-time weather conditions in Jakarta. It fetches data using Airflow’s HTTP integration, processes the response in memory, and then stores key information (e.g., temperature, humidity, weather description, timestamp) into PostgreSQL. This end-to-end pipeline is an excellent demonstration of your skills in data ingestion, processing, and database integration with Airflow.

## Features

- **Real-Time Data Ingestion:** Uses Airflow’s HttpHook to fetch current weather data.
- **In-Memory Data Processing:** Extracts and transforms essential weather data from the API response.
- **Database Integration:** Inserts processed data into a PostgreSQL database using Airflow’s PostgresHook.
- **Automated Workflow:** Airflow DAGs schedule the entire process on an hourly basis.

## Prerequisites
- Docker & Docker Compose: For running Airflow, PostgreSQL, and related services.
- Apache Airflow: Version 2.6.0 or later is recommended.
- PostgreSQL: Can be set up via Docker Compose or your local installation.
- Python 3.x: Required for the DAG scripts.
- Airflow Connections:
    - HTTP Connection (openweather_api):
        - Base URL: http://api.openweathermap.org/data/2.5
        - No authentication required (API key is passed as a parameter).
    - PostgreSQL Connection (postgres_default):
        - Configure with your PostgreSQL credentials.