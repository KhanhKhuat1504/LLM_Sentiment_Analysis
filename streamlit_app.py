import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob

# import mysql.connector

# Connect to MySQL database
#mydb = mysql.connector.connect(
#    host="your_host",
#    user="your_username",
#    password="your_password",
#    database="your_database"
#)

# Create a cursor object to execute SQL queries
#cursor = mydb.cursor()

# Execute SQL query to fetch data from the database
#cursor.execute("SELECT * FROM your_table")
#rows = cursor.fetchall()

# Display fetched data in Streamlit
#if rows:
#    st.write("Fetched data from database:")
#    for row in rows:
#        st.write(row)
#else:
#    st.write("No data available from the database.")


# Load data from CSV
df = pd.read_csv("sentiment_reddit_data.csv")

# Convert 'CreatedTime' to datetime
df['CreatedTime'] = pd.to_datetime(df['CreatedTime'])

# Set the configuration option to disable the PyplotGlobalUseWarning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Calculate sentiment polarity and categorize into negative, neutral, and positive
if 'Text' in df.columns:
    # Replace missing values with empty strings
    df["Text"].fillna("", inplace=True)

    # Calculate sentiment polarity and handle None values
    sentiments = [TextBlob(answer).sentiment.polarity if answer else None for answer in df["Text"]]
    df["Sentiment"] = sentiments

    # Categorize sentiment into negative, neutral, and positive
    df['Sentiment_Category'] = pd.cut(df['Sentiment'], bins=[-1, -0.01, 0.01, 1], labels=['Negative', 'Neutral', 'Positive'])
else:
    st.write("No 'Text' column found in the DataFrame.")

# Main content layout
st.title("DASHBOARD")
st.subheader("Large Language Models Leaderboard using Real-time Mining and Sentiment Analysis")

# Sidebar layout
with st.sidebar:
    st.title("Navigation Panel")
    tabs = st.radio("Select a tab:", ["Direct Feed", "Filtered Feed"])

    if tabs == "Direct Feed":
        st.markdown("# Total Reddit Posts: " + str(len(df)))
        st.subheader("Reddit Post Data")
        st.table(df[['CreatedTime', 'SubmissionID', 'SubmissionTitle', 'Text', 'SubmissionURL', 'Score', 'NumberOfComments', 'SubredditName', 'Sentiment', 'Sentiment_Score']].head(10))
    elif tabs == "Filtered Feed":
        st.subheader("Filter Options")
        selected_subreddit = st.selectbox("Select Subreddit:", df['SubredditName'].unique())
        selected_sentiment = st.selectbox("Select Sentiment Category:", ['Negative', 'Neutral', 'Positive'])
        selected_api = st.selectbox("Select API:", df['API'].unique())
        filtered_df = df[(df['SubredditName'] == selected_subreddit) & 
                         (df['Sentiment_Category'] == selected_sentiment) &
                         (df['API'] == selected_api)]
        st.write(filtered_df.head(10))

# Sentiment Analysis
st.subheader("Sentiment Analysis")

# Basic Statistics
st.subheader("Basic Statistics")
st.write(df.drop(columns=['CreatedTime']).describe())  # Exclude 'CreatedTime' column

# Line graph of Reddit Sentiment Trend by topic
st.subheader("Reddit Sentiment Trend by Topic Over Time")
if 'SubmissionTitle' in df.columns:
    grouped_df = df.groupby([df['CreatedTime'].dt.date, 'Sentiment_Category']).size().unstack(fill_value=0).reset_index()
    fig, ax = plt.subplots()
    ax.plot(grouped_df['CreatedTime'], grouped_df['Negative'], label='Negative', color='red')
    ax.plot(grouped_df['CreatedTime'], grouped_df['Positive'], label='Positive', color='green')
    plt.xlabel('Date')
    plt.ylabel('Number of Posts')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(fig)
else:
    st.write("No 'SubmissionTitle' column found in the DataFrame.")

# Word Cloud
st.subheader("Word Cloud for All Data")
if 'Text' in df.columns:
    df["Text"].fillna("", inplace=True)
    text = ' '.join(df['Text'])
    wordcloud = WordCloud(width=800, height=400, background_color ='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot()
else:
    st.write("No 'Text' column found in the DataFrame.")

# Group by subreddit name and calculate average sentiment polarity
subreddit_sentiments = df.groupby('SubredditName')['Sentiment'].mean().reset_index()

# Bar graph of average sentiment by subreddit
st.subheader("Average Sentiment by Language Model")
if not subreddit_sentiments.empty:
    fig, ax = plt.subplots()
    ax.bar(subreddit_sentiments['SubredditName'], subreddit_sentiments['Sentiment'], color='blue')
    plt.xlabel('Language Model')
    plt.ylabel('Average Sentiment')
    plt.title('Average Sentiment by Language Model')
    plt.xticks(rotation=45, fontsize=6)
    st.pyplot(fig)
else:
    st.write("No data available for average sentiment by language model.")

# Close cursor and database connection
#cursor.close()
#mydb.close()