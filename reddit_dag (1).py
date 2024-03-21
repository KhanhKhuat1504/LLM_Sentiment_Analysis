import pandas as pd
import praw
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Initialize Reddit API
reddit = praw.Reddit(
    client_id="z6qtXsQqW1vN0CDbb2tGwA",
    client_secret="9oDccd73yRKSKqqErOwALpsOdC7xOw",
    user_agent="reddit_data_extract"
)

# Define the function to ingest data from Reddit
def ingest_reddit_data():
    subreddit_names = ['ChatGPT', 'LocalLLaMA', 'GPT3', 'GoogleGeminiAI', 'GeminiAI','Bard','singularity','LargeLanguageModels', 'MistralAI','ClaudeAI','AnthropicClaude','ClaudeAnthropic','GoogleBard']

    # Initialize empty lists to store data
    all_submission_createdtime = []
    all_submission_ids = []
    all_submission_titles = []
    all_submission_text = []
    all_submission_urls = []
    all_search_queries = []
    all_scores = []
    all_numcomments = []
    all_submission_subreddit = []

    # Iterate over each subreddit
    for subreddit_name in subreddit_names:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Search for submissions within the current subreddit
        for submission in subreddit.new(limit=None):
            all_submission_createdtime.append(submission.created_utc)
            all_submission_ids.append(submission.id)
            all_submission_titles.append(submission.title)
            all_submission_text.append(submission.selftext)
            all_submission_urls.append(submission.permalink)
            all_scores.append(submission.score)
            all_numcomments.append(submission.num_comments)
            all_submission_subreddit.append(subreddit_name)

    # Create a DataFrame from the collected data
    data = {
        'CreatedTime': all_submission_createdtime,
        'SubmissionID': all_submission_ids,
        'SubmissionTitle': all_submission_titles,
        'Text': all_submission_text,
        'SubmissionURL': all_submission_urls,
        'Score': all_scores,
        'NumberOfComments': all_numcomments,
        'SubredditName': all_submission_subreddit
    }

    df = pd.DataFrame(data)

    df['CreatedTime'] = pd.to_datetime(df['CreatedTime'], unit='s')  # Convert Unix time to datetime

    return df


def store_dataset():
    reddit_df = ingest_reddit_data()

    # Save to CSV
    reddit_df.to_csv('reddit_data.csv', index=False)


# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'reddit_data',
    default_args=default_args,
    description='Extract data and store',
    schedule_interval='@daily'
)

# Define the PythonOperator to execute the extract task
ingest_reddit_task = PythonOperator(
    task_id='ingest_reddit_data',
    python_callable=ingest_reddit_data,
    dag=dag
)

store_to_csv_task = PythonOperator(
    task_id='store_to_csv',
    python_callable=store_dataset,
    dag=dag
)

ingest_reddit_task>>store_to_csv_task

