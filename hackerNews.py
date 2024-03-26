import requests
import json

# Expanded list of keywords related to various language models and AI technologies
keywords = [
    "Large Language Models",
    "GPT",
    "GPT-2",
    "GPT2",
    "GPT-3",
    "GPT3",
    "GPT-3.5",
    "GPT3.5" "GPT-4",
    "GPT4",
    "OpenAI",
    "ChatGPT",
    "Natural Language Processing",
    "NLP",
    "Transformer",
    "Google BERT",
    "StableLM",
    "Falcon AI",
    "EleutherAI",
    "Language Models",
    "Copilot",
    "Bard",
    "Transformer Models",
    "AI Writing",
    "Text Generation",
    "Language Generation",
    "LaMDA",
    "Generative Pre-trained Transformer",
    "DistilBERT",
    "XLNet",
    "ALBERT",
    "ERNIE",
    "Meta AI",
    "LLaMA",
    "Devin AI",
    "Gemini",
    "PaLM2",
    "Claude AI",
    "Grok",
    "xAI",
]


# Function to normalize text for keyword comparison (lowercase, optionally remove hyphens)
def normalize_text(text):
    return text.lower().replace(
        "-", " "
    )  # Replace hyphens with spaces for standardized comparison


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
            story_response.json() if story_response and story_response.json() else {}
        )

        # Check if the story matches keywords
        if story and any(
            normalize_text(keyword) in normalize_text(story.get("title", ""))
            for keyword in keywords
        ):
            if "kids" in story:
                story["comments"] = fetch_comments(story["kids"])
            filtered_stories.append(story)

# Save the filtered stories with comments to a JSON file
with open("filtered_stories_with_comments.json", "w") as json_file:
    json.dump(filtered_stories, json_file, indent=4)
