import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import kagglehub

load_dotenv()

def download_dataset():
    # Download latest version
    path = kagglehub.dataset_download("shahriarkabir/procurement-kpi-analysis-dataset")
    print("Path to dataset files:", path)
    return path

def upload_data_to_postgres(df, table_name):
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    print(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
    print('Creating connection to Postgres database...')
    
    db_engine = create_engine(
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print('Connection established successfully!')
    print(f'Uploading data to table: {table_name}...')

    # upload to Postgres
    df.to_sql(
        table_name, 
        db_engine, 
        if_exists='replace', 
        index=False
    )

    print(f'Data uploaded successfully to table: {table_name}!')

    db_engine.dispose()
    print('Connection closed successfully!')

path = download_dataset()
df = pd.read_csv(f'{path}/Procurement KPI Analysis Dataset.csv')
df['load_date'] = pd.to_datetime('today').normalize()
upload_data_to_postgres(df, 'procurement_kpi')