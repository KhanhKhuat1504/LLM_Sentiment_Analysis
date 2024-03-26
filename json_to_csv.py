import json
import csv

# Load JSON data from the file
with open("filtered_stories_with_comments.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Prepare CSV files
with open("stories.csv", mode="w", newline="", encoding="utf-8") as stories_file, open(
    "comments.csv", mode="w", newline="", encoding="utf-8"
) as comments_file:

    # Set up CSV writers
    story_writer = csv.writer(stories_file)
    comment_writer = csv.writer(comments_file)

    # Write CSV headers
    story_writer.writerow(
        ["by", "descendants", "id", "score", "time", "title", "type", "url"]
    )
    comment_writer.writerow(["by", "id", "parent", "text", "time", "type", "story_id"])

    # Process each story
    for story in data:
        # Write story details
        story_writer.writerow(
            [
                story.get("by"),
                story.get("descendants"),
                story.get("id"),
                story.get("score"),
                story.get("time"),
                story.get("title"),
                story.get("type"),
                story.get("url"),
            ]
        )

        # Process each comment
        for comment in story.get("comments", []):
            # Recursively write comments and their replies if any
            def write_comment(comment, story_id):
                comment_writer.writerow(
                    [
                        comment.get("by"),
                        comment.get("id"),
                        comment.get("parent"),
                        comment.get("text"),
                        comment.get("time"),
                        comment.get("type"),
                        story_id,
                    ]
                )
                for reply in comment.get("comments", []):
                    write_comment(reply, story_id)  # Recursion for nested comments

            write_comment(comment, story["id"])
