import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from PIL import Image
import mysql.connector



#DATABASE
######################################################################

# Establish connection to MySQL database
try:
    mydb = mysql.connector.connect(
        host="database-1.csopvl4k4p5e.us-east-1.rds.amazonaws.com",
        port=3306,
        database="LLMProject",
        user="admin",
        password="llmtest123"
    )
    st.success("Connected to MySQL database successfully!")
except mysql.connector.Error as err:
    st.error(f"Error connecting to MySQL database: {err}")
    st.stop()

# Create a cursor object to execute SQL queries
cursor = mydb.cursor()

# Execute SQL query to fetch data from the database
query = "SELECT * FROM LLMProject.reddit_hn"  # Replace 'your_table' with the actual table name
try:
    cursor.execute(query)
except mysql.connector.Error as err:
    st.error(f"Error executing SQL query: {err}")
    st.stop()

# Fetch all rows from the query result
rows = cursor.fetchall()

# Convert fetched data to a pandas DataFrame
df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

# Calculate sentiment polarity and categorize into negative, neutral, and positive
if "Text" in df.columns:
    df["Text"].fillna("", inplace=True)
    sentiments = [TextBlob(answer).sentiment.polarity if answer else None for answer in df["Text"]]
    df["Sentiment"] = sentiments
    df["Sentiment_Category"] = pd.cut(df["Sentiment"], bins=[-1, -0.01, 0.01, 1], labels=["Negative", "Neutral", "Positive"])
else:
    st.write("No 'Text' column found in the DataFrame.")

# Load data from CSV before getting sql data
#df = pd.read_csv("sentiment_reddit_data.csv")

######################################################################
#DESIGN 

# Load and display the image at the top of the page
image = Image.open("LLM2.png")
st.image(image, use_column_width=True)

# Define CSS for the decorative header
header_style = f"""
    <style>
        .header {{
            background-image: url('{image}');
            background-size: cover;
            height: 100px; /* Adjust height as needed */
            width: 100%;
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding-top: 30px; /* Adjust vertical alignment */
        }}
    </style>
"""

# Display the decorative header
st.markdown(header_style, unsafe_allow_html=True)

# Set the configuration option to disable the PyplotGlobalUseWarning
st.set_option("deprecation.showPyplotGlobalUse", False)

# Calculate sentiment polarity and categorize into negative, neutral, and positive
if "Text" in df.columns:
    # Replace missing values with empty strings
    df["Text"].fillna("", inplace=True)

    # Calculate sentiment polarity and handle None values
    sentiments = [
        TextBlob(answer).sentiment.polarity if answer else None for answer in df["Text"]
    ]
    df["Sentiment"] = sentiments

    # Categorize sentiment into negative, neutral, and positive
    df["Sentiment_Category"] = pd.cut(
        df["Sentiment"],
        bins=[-1, -0.01, 0.01, 1],
        labels=["Negative", "Neutral", "Positive"],
    )
else:
    st.write("No 'Text' column found in the DataFrame.")

# Sidebar layout
with st.sidebar:
    st.title("Navigation Panel")
    tabs = st.radio("Select a tab:", ["Direct Feed", "Filtered Feed"])

    if tabs == "Direct Feed":
        st.markdown("# Total Reddit Posts: " + str(len(df)))
        st.subheader("Reddit Post Data")
        
        # Display each post inside a bordered box
        for index, row in df.head(10).iterrows():
            with st.expander(f"{row['SubmissionTitle']} - {row['SubmissionID']}", expanded=False):
                st.markdown(
                    f"**Score:** {row['Score']} | **Comments:** {row['NumberOfComments']}"
                    f"\n{row['Text'][:200]}{'...' if len(row['Text']) > 200 else ''}"
                    f"\n[Read More]({row['SubmissionURL']})"
                )
                
    elif tabs == "Filtered Feed":
        st.subheader("Filter Options")
        selected_subreddit = st.selectbox(
            "Select Subreddit:", df["TopicName"].unique()
        )
        selected_sentiment = st.selectbox(
            "Select Sentiment Category:", ["Negative", "Neutral", "Positive"]
        )
        
        # Check if the columns exist in the DataFrame
        if {"TopicName", "Sentiment_Category"}.issubset(df.columns):
            filtered_df = df[
                (df["TopicName"] == selected_subreddit)
                & (df["Sentiment_Category"] == selected_sentiment)
            ]
            
            # Display filtered posts inside a bordered box
            for index, row in filtered_df.head(10).iterrows():
                with st.expander(f"{row['SubmissionTitle']} - {row['SubmissionID']}", expanded=False):
                    st.markdown(
                        f"**Score:** {row['Score']} | **Comments:** {row['NumberOfComments']}"
                        f"\n{row['Text'][:200]}{'...' if len(row['Text']) > 200 else ''}"
                        f"\n[Read More]({row['SubmissionURL']})"
                    )
        else:
            st.write("Required columns not found in the DataFrame. Unable to apply filters.")


# Sentiment Analysis
st.subheader("Sentiment Analysis")

# Basic Statistics
st.subheader("Basic Statistics")
st.write(df.drop(columns=["CreatedTime"]).describe())  # Exclude 'CreatedTime' column

# Line graph of Reddit Sentiment Trend by topic
st.subheader("Reddit Sentiment Trend by Topic Over Time")
if "SubmissionTitle" in df.columns:
    grouped_df = (
        df.groupby([df["CreatedTime"].dt.date, "Sentiment_Category"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    fig, ax = plt.subplots()
    ax.plot(
        grouped_df["CreatedTime"], grouped_df["Negative"], label="Negative", color="red"
    )
    ax.plot(
        grouped_df["CreatedTime"],
        grouped_df["Positive"],
        label="Positive",
        color="green",
    )
    plt.xlabel("Date")
    plt.ylabel("Number of Posts")
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(fig)
else:
    st.write("No 'SubmissionTitle' column found in the DataFrame.")

# Word Cloud
st.subheader("Word Cloud for All Data")
if "Text" in df.columns:
    df["Text"].fillna("", inplace=True)
    text = " ".join(df["Text"])
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        text
    )
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot()
else:
    st.write("No 'Text' column found in the DataFrame.")

# Group by topic name and calculate average sentiment polarity
topic_sentiments = df.groupby("TopicName")["Sentiment"].mean().reset_index()

# Bar graph of average sentiment by topic
st.subheader("Average Sentiment by Topic")
if not topic_sentiments.empty:
    fig, ax = plt.subplots()
    ax.bar(
        topic_sentiments["TopicName"],
        topic_sentiments["Sentiment"],
        color="blue",
    )
    plt.xlabel("Topic")
    plt.ylabel("Average Sentiment")
    plt.title("Average Sentiment by Topic")
    plt.xticks(rotation=45, fontsize=6)
    st.pyplot(fig)
else:
    st.write("No data available for average sentiment by topic.")


# Close cursor and connection to MySQL database
cursor.close()
mydb.close()