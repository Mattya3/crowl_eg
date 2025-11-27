import os
import boto3
import time
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()

TABLE_NAME = os.environ.get('SENT_ARTICLES_TABLE', 'SentArticles')
# Initialize DynamoDB resource. 
# Note: When running locally with sam local, you might need to point to a local DynamoDB or use a real one.
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

TTL_DAYS = 30

def filter_new_articles(articles):
    """
    Check DynamoDB to see if articles have been sent recently.
    Returns a list of articles that are NOT in the DB.
    """
    new_articles = []
    
    # Batch get item is more efficient but for simplicity and small batch size, loop get is okay or use batch_get_item
    # Since we need to check existence, we can try to get item.
    
    # Optimization: Use batch_get_item if checking many. For 20 items, loop is acceptable but batch is better.
    # Let's use a simple loop for now as we might not have many candidates after filtering.
    
    for article in articles:
        url = article['url']
        try:
            response = table.get_item(Key={'url': url})
            if 'Item' not in response:
                new_articles.append(article)
        except ClientError as e:
            logger.error(f"DynamoDB error checking {url}: {e}")
            # If DB fails, maybe safe to skip or assume new? Let's skip to avoid spam.
            continue
            
    return new_articles

def save_sent_articles(articles):
    """
    Save sent articles to DynamoDB with TTL.
    """
    expires_at = int(time.time()) + (TTL_DAYS * 24 * 60 * 60)
    
    with table.batch_writer() as batch:
        for article in articles:
            try:
                batch.put_item(Item={
                    'url': article['url'],
                    'title': article['title'],
                    'sent_at': int(time.time()),
                    'expires_at': expires_at
                })
            except ClientError as e:
                logger.error(f"Failed to save article {article['url']}: {e}")
