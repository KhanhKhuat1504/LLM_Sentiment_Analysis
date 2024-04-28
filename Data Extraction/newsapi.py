import requests
import json


def get_news(api_key, keywords):
    url = "https://newsapi.org/v2/everything"
    all_articles = []

    for keyword in keywords:
        params = {
            "q": keyword,
            "apiKey": api_key,
            "language": "en",
            "pageSize": 100,  # Increase the page size to retrieve more articles
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            all_articles.extend(articles)
            print(f"{len(articles)} articles found for '{keyword}'")
        else:
            print(
                f"Failed to fetch articles for {keyword}. Status Code: {response.status_code}"
            )

    return all_articles


# Replace 'your_api_key' with your actual News API key
api_key = "f859af4f943e4d649f5534c3347962b1"
keywords = ["VASA-1"]

articles = get_news(api_key, keywords)

# Save all articles to a single JSON file
with open("news_articles_3.json", "w", encoding="utf-8") as file:
    json.dump(articles, file, ensure_ascii=False, indent=4)

print(f"All articles saved to news_articles_3.json")
