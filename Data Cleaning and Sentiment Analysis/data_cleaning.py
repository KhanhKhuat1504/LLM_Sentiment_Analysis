import pandas as pd
import re
from sqlalchemy import create_engine

# Define the database connection URI
# Replace 'username', 'password', 'host', 'port', and 'database_name' with your MySQL database credentials
db_connection_uri = (
    "mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
)
engine = create_engine(db_connection_uri)


# Define a function to clean text by removing special characters and unicode
def clean_text(text):
    # Normalize unicode characters to ASCII equivalents when possible
    text = text.encode("ascii", "ignore").decode("ascii")
    # Remove remaining special characters
    text = re.sub(r"[^a-zA-Z0-9\s,.?!]", "", text)
    return text


# Define a function to load and clean the dataset from MySQL database
def load_and_clean_data(db_connection_uri):
    # Create a SQLAlchemy engine
    engine = create_engine(db_connection_uri)

    # Load the dataset from MySQL table
    query = "SELECT * FROM reddit_hn"
    df = pd.read_sql_query(query, engine)

    # Drop rows where 'Text' have missing values
    df.dropna(subset=["Text"], inplace=True)

    # Clean the 'SubmissionTitle' and 'Text' columns
    df["SubmissionTitle"] = df["SubmissionTitle"].apply(clean_text)
    df["Text"] = df["Text"].apply(clean_text)

    return df


# Call the function to load and clean the data
cleaned_df = load_and_clean_data(db_connection_uri)
print(cleaned_df.head())  # Display the first few rows of the cleaned dataframe

# Save the cleaned dataframe to a new table in MySQL database
cleaned_df.to_sql("cleaned_reddit_data", engine, index=False, if_exists="replace")
