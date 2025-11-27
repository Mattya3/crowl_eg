import os
import requests
import logging

logger = logging.getLogger()

QIITA_API_ENDPOINT = "https://qiita.com/api/v2/items"
QIITA_ACCESS_TOKEN = os.environ.get('QIITA_ACCESS_TOKEN')

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
        'page': 1
    }

    try:
        response = requests.get(QIITA_API_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        items = response.json()
        
        articles = []
        for item in items:
            articles.append({
                'title': item['title'],
                'url': item['url'],
                'likes_count': item['likes_count'],
                'created_at': item['created_at'],
                'user': item['user']['id']
            })
        
        # Sort by likes_count descending (simple ranking logic)
        articles.sort(key=lambda x: x['likes_count'], reverse=True)
        
        return articles

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch from Qiita: {e}")
        return []
