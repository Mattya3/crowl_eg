import feedparser
import logging
import datetime
from dateutil import parser

logger = logging.getLogger()

# Zenn Trend Feed
ZENN_FEED_URL = "https://zenn.dev/feed"

def fetch_zenn_articles(count=20):
    """
    Fetch articles from Zenn RSS feed.
    """
    try:
        feed = feedparser.parse(ZENN_FEED_URL)
        articles = []
        
        for entry in feed.entries[:count]:
            # Zenn RSS entries usually have 'title', 'link', 'published', 'author'
            # Note: Zenn RSS doesn't provide 'likes' count directly. 
            # We might need to scrape or just rely on the fact that it's the trend feed.
            # For now, we'll treat them as having a default 'score' or just use them as is.
            
            published_at = entry.get('published', '')
            
            articles.append({
                'title': entry.title,
                'url': entry.link,
                'likes_count': 0, # Placeholder as RSS doesn't have likes
                'source': 'Zenn',
                'created_at': published_at,
                'user': entry.get('author', 'unknown')
            })
            
        return articles

    except Exception as e:
        logger.error(f"Failed to fetch from Zenn: {e}")
        return []
