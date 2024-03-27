from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from reddit_data import extract_reddit_data
from hackernews_data import extract_hn_data
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
import numpy as np


# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'Data_ingestion',
    default_args=default_args,
    description='Extract Reddit data',
    schedule_interval=None,  # Set to None to disable scheduling
)


def combine_datasets(**kwargs):
    ti = kwargs['ti']
    reddit_df = ti.xcom_pull(task_ids=kwargs['reddit_df_task_id'])
    hn_df = ti.xcom_pull(task_ids=kwargs['hn_df_task_id'])

    # Read CSV files into DataFrames
    #reddit_df = pd.read_csv("/mnt/home/axm1849/airflow/reddit_data.csv")
    #hn_df = pd.read_csv("/mnt/home/axm1849/airflow/hn_data.csv")

    # Concatenate the DataFrames
    combined_df = pd.concat([reddit_df, hn_df], ignore_index=True)
    return combined_df

# Function to clean the dataset
def clean_dataset(**kwargs):
    # Convert 'CreatedTime' to datetime
    #df['CreatedTime'] = pd.to_datetime(df['CreatedTime'], unit='s')
    # Retrieve the combined dataset from XCom
    ti = kwargs['ti']
    combined_data = ti.xcom_pull(task_ids='Combine_datasets')
    # Convert combined dataset to DataFrame
    df = pd.DataFrame(combined_data)
    # Replace empty strings with pd.NA
    df['Text'] = df['Text'].replace('', pd.NA)
    
    # Replace NaN with 'NULL' string for MySQL compatibility
    df['Text'] = df['Text'].fillna('NULL')
    
    return df

def load_database(**kwargs):
    # Retrieve the cleaned dataset from XCom
    ti = kwargs['ti']
    cleaned_data = ti.xcom_pull(task_ids='Clean_dataset')
    
    # Connect to your MySQL database using the provided connection string
    connection_string = "mysql+pymysql://root:90FFupOIIDg2Sw@129.22.23.234:3312/airflow_db"
    engine = create_engine(connection_string)
    
    # Manually create table in MySQL
    table_name = 'reddit_hn'

    create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                CreatedTime DATETIME,
                SubmissionID VARCHAR(255),
                SubmissionTitle TEXT,
                Text TEXT,
                SubmissionURL TEXT,
                Score INT,
                NumberOfComments INT,
                TopicName VARCHAR(255),
                PRIMARY KEY (SubmissionID)
            )
            """

    # Execute the CREATE TABLE statement
    with engine.connect() as connection:
        connection.execute(create_table_sql)
    
    # Iterate through DataFrame rows and insert into MySQL table
    with engine.connect() as connection:
        for index, row in cleaned_data.iterrows():
            # Check if the SubmissionID already exists in the table
            submission_id = row['SubmissionID']
            check_sql = f"SELECT COUNT(*) FROM {table_name} WHERE SubmissionID = '{submission_id}'"
            result = connection.execute(check_sql).fetchone()
            
            # If the SubmissionID does not exist, insert the row into the table
            if result[0] == 0:
                # Construct SQL INSERT statement
                insert_sql = f"""
                INSERT INTO {table_name} (CreatedTime, SubmissionID, SubmissionTitle, Text, SubmissionURL, Score, NumberOfComments, TopicName)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Execute SQL statement to insert the row
                connection.execute(insert_sql, (row['CreatedTime'], row['SubmissionID'], row['SubmissionTitle'], row['Text'], row['SubmissionURL'], row['Score'], row['NumberOfComments'], row['TopicName']))


# Define the task that calls the extract_reddit_data function
extract_redditdata_task = PythonOperator(
    task_id='Ingest_reddit_data',
    python_callable=extract_reddit_data,
    dag=dag,
)

# Define the task that calls the extract_hn_data function
extract_hndata_task = PythonOperator(
    task_id='Ingest_hackernews_data',
    python_callable=extract_hn_data,
    dag=dag,
)

combine_datasets_task = PythonOperator(
    task_id='Combine_datasets',
    python_callable=combine_datasets,
    op_kwargs={'reddit_df_task_id': 'Ingest_reddit_data',
               'hn_df_task_id': 'Ingest_hackernews_data'},
    dag=dag,
)


clean_dataset_task = PythonOperator(
    task_id='Clean_dataset',
    python_callable=clean_dataset,
    provide_context=True,
    dag=dag,
)

load_database_task = PythonOperator(
task_id='load_database',
python_callable=load_database,
provide_context=True,
dag=dag,
)

# Set task dependencies
[extract_redditdata_task,extract_hndata_task] >> combine_datasets_task >> clean_dataset_task >> load_database_task


