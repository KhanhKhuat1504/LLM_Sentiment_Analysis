import praw
import pandas as pd
from datetime import datetime, timedelta


def extract_reddit_data():
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id="z6qtXsQqW1vN0CDbb2tGwA",
        client_secret="9oDccd73yRKSKqqErOwALpsOdC7xOw",
        user_agent="Scraper",
    )

    subreddit_names = [
        "ChatGPT",
        "ChatGPTPro",
        "StableDiffusion",
        "singularity",
        "CharacterAI",
        "LocalLLaMA",
        "dalle2",
        "GPT3",
        "GoogleGeminiAI",
        "GeminiAI",
        "Bard",
        "LargeLanguageModels",
        "MistralAI",
        "ClaudeAI",
        "LocalLLM",
        "OpenAI"
    ]

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
        "CreatedTime": all_submission_createdtime,
        "SubmissionID": all_submission_ids,
        "SubmissionTitle": all_submission_titles,
        "Text": all_submission_text,
        "SubmissionURL": all_submission_urls,
        "Score": all_scores,
        "NumberOfComments": all_numcomments,
        "TopicName": all_submission_subreddit,
    }

    df = pd.DataFrame(data)

    df["CreatedTime"] = pd.to_datetime(df["CreatedTime"], unit="s")
    df["SubmissionID"] = df["SubmissionID"].astype(str)

    # df.to_csv("reddit_data.csv", index=False)
    return df
