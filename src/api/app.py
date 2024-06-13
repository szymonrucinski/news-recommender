from fastapi import FastAPI, Response
from feedgen.feed import FeedGenerator
import yaml
import feedparser
import os
import requests
from pathlib import Path

app = FastAPI()


def load_feeds_from_yaml(yaml_file):
    with open(yaml_file, "r") as file:
        config = yaml.safe_load(file)
    return config["feeds"]


def fetch_feed_entries(feed_urls):
    entries = []
    for url in feed_urls:
        response = requests.get(url)
        feed = feedparser.parse(response.content)
        entries.extend(feed.entries)
    return entries


@app.get("/rss")
async def rss():
    # Determine the absolute path to the config/feeds.yaml file using pathlib
    base_path = Path(__file__).resolve().parents[2]
    config_path = base_path / "config" / "feeds.yaml"
    feed_urls = load_feeds_from_yaml(config_path)
    entries = fetch_feed_entries(feed_urls)

    fg = FeedGenerator()
    fg.title("Aggregated RSS Feed")
    fg.link(href="http://example.com/rss", rel="self")
    fg.description("This is an aggregated RSS feed from multiple sources.")

    for entry in entries:
        fe = fg.add_entry()
        fe.id(entry.id if "id" in entry else entry.link)
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.summary if "summary" in entry else "")

    rss_feed = fg.rss_str(pretty=True)
    return Response(content=rss_feed, media_type="application/rss+xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
