import pandas as pd
from transformers import pipeline
from sqlalchemy import create_engine

# Load your data
# Create database engine to connect to MySQL
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# Load your data from MySQL database
df = pd.read_sql_table("cleaned_reddit_data", con=engine)

# Initialize the sentiment-analysis pipeline with a model
# Specify the use of DistilBERT for sentiment analysis
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
# Note: This approach truncates text to 512 characters for simplicity
results = [get_sentiment(text) for text in df["Text"]]

# Extract sentiment and score from results and add them to the dataframe
df["Sentiment"] = [result["label"] for result in results]
df["Sentiment_Score"] = [result["score"] for result in results]

# Save the updated dataframe to a new table

# Use if_exists='replace' to replace existing table, or 'append' to add data to an existing table (if it exists)
df.to_sql("sentiment_analysis", con=engine, index=False, if_exists="replace")
