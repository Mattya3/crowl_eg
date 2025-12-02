import os
import requests
import logging
import datetime
import math
from dateutil import parser
from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq

logger = logging.getLogger()

QIITA_API_ENDPOINT = "https://qiita.com/api/v2/items"
QIITA_ACCESS_TOKEN = os.environ.get('QIITA_ACCESS_TOKEN')

def fetch_page(page, headers, params):
    """
    Fetch a single page of articles.
    """
    local_params = params.copy()
    local_params['page'] = page
    try:
        response = requests.get(QIITA_API_ENDPOINT, headers=headers, params=local_params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching Qiita articles at page {page}: {e}")
        return []

def fetch_articles(query="tag:Python", count=20):
    """
    Fetch articles from Qiita based on query.
    """
    headers = {}
    if QIITA_ACCESS_TOKEN:
        headers['Authorization'] = f'Bearer {QIITA_ACCESS_TOKEN}'

    params = {
        'query': query,
        'per_page': count,
    }

    all_articles = []
    max_pages = 10 # Fetch up to 1000 articles (100 * 10) - Reduced from 20 for performance
    
    # Use ThreadPoolExecutor for parallel fetching
    # Limit max_workers to 5 to be safe with API limits
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {
            executor.submit(fetch_page, page, headers, params): page
            for page in range(1, max_pages + 1)
        }
        
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                items = future.result()
                if not items:
                    continue
                    
                for item in items:
                    # Calculate Trend Score (Hacker News Algorithm)
                    # Score = (P - 1) / (T + 2)^G
                    # P = likes_count, T = hours since creation, G = 1.8
                    likes = int(item['likes_count'])
                    created_at = parser.parse(item['created_at'])
                    now = datetime.datetime.now(datetime.timezone.utc)
                    
                    # Ensure created_at is timezone aware
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                    
                    diff = now - created_at
                    hours = diff.total_seconds() / 3600
                    
                    # Avoid negative hours (just in case of clock skew)
                    if hours < 0:
                        hours = 0
                        
                    trend_score = (likes - 1) / math.pow((hours + 2), 1.8)

                    all_articles.append({
                        'title': item['title'],
                        'url': item['url'],
                        'likes_count': item['likes_count'],
                        'stocks_count': item['stocks_count'],
                        'created_at': item['created_at'],
                        'user': item['user']['id'],
                        'trend_score': trend_score
                    })
            except Exception as e:
                logger.error(f"Exception processing page {page}: {e}")
        
    # Use heapq to get top K articles efficiently
    top_articles = heapq.nlargest(count, all_articles, key=lambda x: x.get('trend_score', 0))
    
    return top_articles
