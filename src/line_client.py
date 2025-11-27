import os
import requests
import logging
import json

logger = logging.getLogger()

LINE_MESSAGING_API_URL = "https://api.line.me/v2/bot/message/broadcast"
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
# USER_ID is not needed for broadcast

def send_line_message(articles):
    """
    Send articles to ALL friends via LINE Broadcast.
    """
    if not CHANNEL_ACCESS_TOKEN:
        logger.error("LINE_CHANNEL_ACCESS_TOKEN not found.")
        return False

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }

    # Construct Flex Message or simple text
    messages = []
    
    # Construct single text message with all articles
    header = "📅 Today's Recommended Articles\n"
    body = ""
    
    for i, article in enumerate(articles, 1):
        body += f"\n{i}. [{article['source']}] {article['title']}\n{article['url']}\n"

    full_text = header + body

    messages.append({
        "type": "text",
        "text": full_text.strip()
    })

    payload = {
        "messages": messages
    }

    try:
        response = requests.post(LINE_MESSAGING_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send to LINE: {e}")
        if 'response' in locals() and response is not None:
             logger.error(f"Response: {response.text}")
        return False
