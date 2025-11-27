import json
import os
import logging
import random
import math
import datetime
from qiita_client import fetch_articles as fetch_qiita_articles
from zenn_client import fetch_zenn_articles
from db_client import filter_new_articles, save_sent_articles
from line_client import send_line_message

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Config
ARTICLE_COUNT = int(os.environ.get('ARTICLE_COUNT', 3))

def lambda_handler(event, context):
    """
    Lambda handler to fetch articles, filter duplicates, and send to LINE.
    """
    logger.info("Starting article recommendation process.")
    
    try:
        # 1. Fetch articles from multiple sources
        # Qiita: Recently Popular (Last 7 days, sorted by likes)
        # Construct query for recent articles
        days_ago = 7
        target_date = (datetime.date.today() - datetime.timedelta(days=days_ago)).isoformat()
        qiita_query = f"created:>{target_date} stocks:>10" # Filter for some popularity to ensure quality
        
        qiita_articles = fetch_qiita_articles(query=qiita_query, count=100) # Fetch max per page to get best candidates
        for a in qiita_articles:
            a['source'] = 'Qiita'
        
        # Zenn: Trend
        zenn_articles = fetch_zenn_articles(count=50)
        
        all_articles = qiita_articles + zenn_articles
        logger.info(f"Fetched {len(all_articles)} articles (Qiita: {len(qiita_articles)}, Zenn: {len(zenn_articles)}).")

        # 2. Filter duplicates
        new_articles = filter_new_articles(all_articles)
        logger.info(f"Found {len(new_articles)} new articles after filtering.")

        if not new_articles:
            logger.info("No new articles to send.")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No new articles found."})
            }

        # 3. Select articles
        # Logic:
        # k = ceil(N / 3)
        # Top k from Qiita
        # Top k from Zenn
        # Remainder (N - 2k) from random
        
        k = math.ceil(ARTICLE_COUNT / 3)
        
        qiita_candidates = [a for a in new_articles if a['source'] == 'Qiita']
        zenn_candidates = [a for a in new_articles if a['source'] == 'Zenn']
        
        # Sort Qiita by likes (already sorted by fetcher usually, but ensure it)
        qiita_candidates.sort(key=lambda x: x.get('likes_count', 0), reverse=True)
        # Zenn is from RSS trend, so order is roughly trend rank.
        
        selected_articles = []
        
        # Select Top k from Qiita
        for _ in range(k):
            if qiita_candidates:
                selected_articles.append(qiita_candidates.pop(0))
                
        # Select Top k from Zenn
        for _ in range(k):
            if zenn_candidates:
                selected_articles.append(zenn_candidates.pop(0))
        
        # Fill the rest (up to ARTICLE_COUNT) from remaining
        remaining = qiita_candidates + zenn_candidates
        random.shuffle(remaining)
        
        while len(selected_articles) < ARTICLE_COUNT and remaining:
            selected_articles.append(remaining.pop(0))
            
        # Trim if somehow we exceeded (e.g. if k is large but N is small? No, k=ceil(N/3) so 2k <= 2N/3 + 2 < N usually, unless N=1 -> k=1 -> 2k=2 > 1. Ah!)
        # Wait, if N=1, k=1. We select 1 Qiita, 1 Zenn. Total 2. Exceeds N=1.
        # The user said: "k=n/3 rounded up. Remainder n-2k random."
        # If N=1, k=1. n-2k = 1-2 = -1. 
        # So if N=1, we pick 2 items? That violates N.
        # I should strictly limit to ARTICLE_COUNT at the end.
        
        selected_articles = selected_articles[:ARTICLE_COUNT]
        
        # 4. Send to LINE
        message_sent = send_line_message(selected_articles)
        
        if message_sent:
            # 5. Save to DB
            save_sent_articles(selected_articles)
            logger.info(f"Sent and saved {len(selected_articles)} articles.")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Articles sent successfully."})
            }
        else:
            logger.error("Failed to send message to LINE.")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Failed to send LINE message."})
            }

    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error"})
        }
