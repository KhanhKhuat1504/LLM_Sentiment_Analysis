import pandas as pd
import re
from sqlalchemy import create_engine


def load_clean_and_save_data(username, password, host, port, database_name, table_name):
    """
    Loads data from a MySQL table, cleans the text data, and saves the cleaned data back to a new table.

    Parameters:
    - username: MySQL username
    - password: MySQL password
    - host: MySQL host
    - port: MySQL port
    - database_name: Name of the MySQL database
    - table_name: Name of the table to load data from
    """
    # Define the database connection URI
    db_connection_uri = (
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
    )

    # Create a SQLAlchemy engine
    engine = create_engine(db_connection_uri)

    # Function to clean text by removing special characters and unicode
    def clean_text(text):
        text = text.encode("ascii", "ignore").decode(
            "ascii"
        )  # Normalize unicode characters
        text = re.sub(r"[^a-zA-Z0-9\s,.?!]", "", text)  # Remove special characters
        return text

    # Load the dataset from MySQL table
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)

    # Drop rows where 'Text' have missing values
    df.dropna(subset=["Text"], inplace=True)

    # Clean the 'SubmissionTitle' and 'Text' columns
    df["SubmissionTitle"] = df["SubmissionTitle"].apply(clean_text)
    df["Text"] = df["Text"].apply(clean_text)

    # Save the cleaned dataframe to a new table in MySQL database
    cleaned_table_name = "cleaned_" + table_name
    df.to_sql(cleaned_table_name, engine, index=False, if_exists="replace")

    # Optionally, return or print a message to indicate completion
    print(f"Data loaded, cleaned, and saved to {cleaned_table_name} successfully.")


# Example usage
# load_clean_and_save_data('username', 'password', 'host', 'port', 'database_name', 'reddit_hn')
