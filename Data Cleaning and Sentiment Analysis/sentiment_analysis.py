import pandas as pd
from transformers import pipeline
from sqlalchemy import create_engine


def perform_sentiment_analysis(
    db_user, db_password, db_host, db_name, input_table_name, output_table_name
):
    """
    Loads data from a specified MySQL table, performs sentiment analysis, and saves the results to another table.

    Parameters:
    - db_user: Database username
    - db_password: Database password
    - db_host: Database host
    - db_name: Database name
    - input_table_name: Name of the table from which to load data
    - output_table_name: Name of the table where analysis results will be saved
    """
    # Create database engine to connect to MySQL
    engine = create_engine(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )

    # Load your data from MySQL database
    df = pd.read_sql_table(input_table_name, con=engine)

    # Initialize the sentiment-analysis pipeline with a model
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    # Define a wrapper function for sentiment analysis that includes error handling
    def get_sentiment(text):
        try:
            # Directly passing text to the pipeline; it handles tokenization and truncation
            result = sentiment_pipeline(
                text[:512]
            )  # Manually truncating texts longer than 512 characters
            return result[0]
        except Exception as e:
            print(f"Error processing text: {e}")
            return {"label": "ERROR", "score": 0}

    # Apply sentiment analysis to the 'Text' column
    results = [get_sentiment(text) for text in df["Text"]]

    # Extract sentiment and score from results and add them to the dataframe
    df["Sentiment"] = [result["label"] for result in results]
    df["Sentiment_Score"] = [result["score"] for result in results]

    # Save the updated dataframe to a new table
    df.to_sql(output_table_name, con=engine, index=False, if_exists="replace")

    # Optionally, return or print a message to indicate completion
    print(f"Sentiment analysis completed and results saved to {output_table_name}.")


# Example usage (replace placeholder values with actual database credentials and table names)
# perform_sentiment_analysis('db_user', 'db_password', 'db_host', 'db_name', 'cleaned_reddit_data', 'sentiment_analysis_results')
