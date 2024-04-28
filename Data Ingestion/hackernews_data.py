import requests
import json
import pandas as pd


def extract_hn_data():
    # Expanded list of keywords related to various language models and AI technologies
    keywords = ["VASA-1", "DBRX", "Devin AI"]

    # Function to normalize text for keyword comparison (lowercase, optionally remove hyphens)
    def normalize_text(text):
        return text.lower().replace("-", " ")

    # Define base URL for Hacker News API
    base_url = "https://hacker-news.firebaseio.com/v0/"

    # Function to recursively fetch comments (unchanged)
    def fetch_comments(comment_ids):
        comments = []
        for comment_id in comment_ids:
            comment_url = f"{base_url}item/{comment_id}.json"
            comment_response = requests.get(comment_url)
            comment = comment_response.json()
            if comment and "kids" in comment:
                comment["comments"] = fetch_comments(comment["kids"])
            comments.append(comment)
        return comments

    # Fetch top stories and filter them by keywords
    categories = [
        "topstories",
        "newstories",
        "beststories",
        "askstories",
        "showstories",
    ]

    filtered_stories = []

    # Fetch and filter stories from each category
    for category in categories:
        url = f"{base_url}{category}.json"
        response = requests.get(url)
        story_ids = response.json() if response and response.json() else []

        for story_id in story_ids[:100000]:  # Adjust the number of stories as needed
            story_url = f"{base_url}item/{story_id}.json"
            story_response = requests.get(story_url)
            story = (
                story_response.json()
                if story_response and story_response.json()
                else {}
            )

            # Check if the story matches keywords
            if story and any(
                normalize_text(keyword) in normalize_text(story.get("title", ""))
                for keyword in keywords
            ):
                # Add a new key "keywords" to story to store the matched keywords
                story["keywords"] = [
                    keyword
                    for keyword in keywords
                    if normalize_text(keyword) in normalize_text(story.get("title", ""))
                ]
                if "kids" in story:
                    story["comments"] = fetch_comments(story["kids"])
                filtered_stories.append(story)

    # Save the filtered stories with comments to a JSON file
    with open("filtered_stories_with_comments.json", "w") as json_file:
        json.dump(filtered_stories, json_file, indent=4)

    # Load JSON data from the file
    with open("filtered_stories_with_comments.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Initialize empty lists to store data
    stories_data = []
    comments_data = []

    # Process each story
    for story in data:
        # Extracting keywords from the story
        story_keywords = ", ".join(story.get("keywords", []))

        # Append story details to stories_data list
        stories_data.append(
            [
                story.get("descendants"),
                story.get("id"),
                story.get("score"),
                story.get("title"),
                story.get("url"),
                story_keywords,  # Add keywords attribute
            ]
        )

        # Process each comment
        for comment in story.get("comments", []):
            # Append comment details to comments_data list
            comments_data.append(
                [
                    comment.get("id"),
                    comment.get("text"),
                    comment.get("time"),
                    story["id"],
                ]
            )

    # Create DataFrame for stories
    stories_df = pd.DataFrame(
        stories_data,
        columns=["descendants", "story_id", "score", "title", "url", "keywords"],
    )

    # Create DataFrame for comments
    comments_df = pd.DataFrame(
        comments_data, columns=["comment_id", "text", "time", "story_id"]
    )

    stories_df = stories_df.drop_duplicates(subset=["story_id"])

    comments_df = comments_df.drop_duplicates(subset=["comment_id"])

    new_df = comments_df.merge(stories_df, on="story_id", how="left")
    new_df = new_df.drop(columns=["story_id"])

    new_df = new_df.reindex(
        columns=[
            "time",  # CreatedTime
            "comment_id",  # SubmissionID
            "title",  # SubmissionTitle
            "text",  # Text
            "url",  # SubmissionURL
            "score",  # Score
            "descendants",  # NumberOfComments
            "keywords",  # TopicName
        ]
    )

    # Rename columns
    new_df = new_df.rename(
        columns={
            "time": "CreatedTime",
            "comment_id": "SubmissionID",
            "title": "SubmissionTitle",
            "text": "Text",
            "url": "SubmissionURL",
            "score": "Score",
            "descendants": "NumberOfComments",
            "keywords": "TopicName",
        }
    )

    new_df["CreatedTime"] = pd.to_datetime(new_df["CreatedTime"], unit="s")
    new_df["SubmissionID"] = new_df["SubmissionID"].astype(str)
    # new_df.to_csv("hn_data.csv", index=False)

    return new_df
