import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from wordcloud import WordCloud
from textblob import TextBlob

# Load data from CSV
df = pd.read_csv("sentiment_reddit_data.csv")

# Convert 'CreatedTime' to datetime
df['CreatedTime'] = pd.to_datetime(df['CreatedTime'])

# Set the configuration option to disable the PyplotGlobalUseWarning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Sidebar layout
st.sidebar.title("Top 15 Most Popular Topics")
if 'Subject' in df.columns:  # Checking if 'Subject' column exists in the DataFrame
    top_topics = df['Subject'].value_counts().head(15).index.tolist()
    st.sidebar.write(top_topics)
else:
    st.sidebar.write("No 'Subject' column found in the DataFrame.")

# Main content layout
st.title("LLM Sentiment Analysis")
st.subheader("Large Language Models Leaderboard using Real-time Mining and Sentiment Analysis")

# Display total number of Reddit posts
st.markdown("# Total Reddit Posts: " + str(len(df)))

# Sentiment Analysis
st.subheader("Sentiment Analysis")
# Assuming 'Text' column exists in the DataFrame
if 'Text' in df.columns:
    # Replace missing values with empty strings
    df["Text"].fillna("", inplace=True)
    
    # Calculate sentiment polarity and handle None values
    sentiments = [TextBlob(answer).sentiment.polarity if answer else None for answer in df["Text"]]
    df["Sentiment"] = sentiments

    # Categorize sentiment into negative, neutral, and positive
    df['Sentiment_Category'] = pd.cut(df['Sentiment'], bins=[-1, -0.01, 0.01, 1], labels=['Negative', 'Neutral', 'Positive'])

    # Basic Statistics
    st.subheader("Basic Statistics")
    st.write(df.drop(columns=['CreatedTime']).describe())  # Exclude 'CreatedTime' column

    # Display the table
    with st.expander("Show Reddit Post Data"):
        st.table(df[['CreatedTime', 'SubmissionID', 'SubmissionTitle', 'Text', 'SubmissionURL', 'Score', 'NumberOfComments', 'SubredditName', 'Sentiment', 'Sentiment_Score']].head(10))

    # Line graph of Reddit Sentiment Trend by topic
    st.subheader("Reddit Sentiment Trend by Topic Over Time")
    # Assuming the topics are stored in the 'SubmissionTitle' column
    if 'SubmissionTitle' in df.columns:
        # Group by day and calculate mean sentiment polarity, handling None values
        grouped_df = df.groupby([df['CreatedTime'].dt.date, 'Sentiment_Category']).size().unstack(fill_value=0).reset_index()

        # Plot sentiment polarity over time
        fig, ax = plt.subplots()
        ax.plot(grouped_df['CreatedTime'], grouped_df['Negative'], label='Negative', color='red')
        ax.plot(grouped_df['CreatedTime'], grouped_df['Neutral'], label='Neutral', color='yellow')
        ax.plot(grouped_df['CreatedTime'], grouped_df['Positive'], label='Positive', color='green')

        plt.xlabel('Date')
        plt.ylabel('Number of Posts')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.legend()
        st.pyplot(fig)
    else:
        st.write("No 'SubmissionTitle' column found in the DataFrame.")

    # Word Cloud
    if 'Text' in df.columns:
        # Filter the DataFrame based on the selected topic
        if 'Subject' in df.columns:
            selected_topic = st.sidebar.selectbox("Select a topic:", top_topics)
            filtered_df = df[df['Subject'] == selected_topic]
        else:
            filtered_df = df
        
        # Replace missing values with empty strings
        filtered_df["Text"].fillna("", inplace=True)
        
        # Tokenize the text and generate word frequencies
        text = ' '.join(filtered_df['Text'])
        wordcloud = WordCloud(width=800, height=400, background_color ='white').generate(text)
        
        # Display the word cloud
        st.subheader("Word Cloud for Selected Topic")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot()
else:
    st.write("No 'Text' column found in the DataFrame.")

# Group by subreddit name and calculate average sentiment polarity
subreddit_sentiments = df.groupby('SubredditName')['Sentiment'].mean().reset_index()

# Bar graph of average sentiment by subreddit (assuming language model names are used as subreddit names)
st.subheader("Average Sentiment by Language Model")
if not subreddit_sentiments.empty:
    fig, ax = plt.subplots()
    ax.bar(subreddit_sentiments['SubredditName'], subreddit_sentiments['Sentiment'], color='blue')
    plt.xlabel('Language Model')
    plt.ylabel('Average Sentiment')
    plt.title('Average Sentiment by Language Model')
    plt.xticks(rotation=45, fontsize=6)  # Rotate x-axis labels and set font size
    st.pyplot(fig)
else:
    st.write("No data available for average sentiment by language model.")

# Can do additional topic modeling, LDA/NMF 
#Entity Recognition (expressed w avg sentiment bar graph)
    
