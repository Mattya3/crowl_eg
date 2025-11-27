import boto3
import sys

def clear_table(table_name='SentArticles'):
    """
    Clears all items from the specified DynamoDB table.
    """
    print(f"Connecting to DynamoDB table: {table_name}...")
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Scan to get all items (Note: Scan is expensive, but fine for this maintenance task)
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            print("Table is already empty.")
            return

        print(f"Found {len(items)} items. Deleting...")
        
        with table.batch_writer() as batch:
            for item in items:
                # Assuming 'url' is the partition key based on template.yaml
                batch.delete_item(Key={'url': item['url']})
                
        print("Successfully cleared the table.")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have AWS credentials configured (aws configure).")

if __name__ == "__main__":
    clear_table()
