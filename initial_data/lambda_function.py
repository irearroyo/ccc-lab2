import json
import boto3
import os
from decimal import Decimal

# Initialize DynamoDB client (low-level API)
dynamodb = boto3.client('dynamodb')

# Get table name from environment variable or use default
table_name = os.environ.get('TABLE_NAME', 'ProductInventory')

def lambda_handler(event, context):
    """
    Lambda function to search products in DynamoDB table.
    Supports filtering by category, name, minPrice, and maxPrice.
    """
    print(f"Received event: {json.dumps(event)}")
    
    # CORS headers - Allow web browsers to call this API from different domains
    # Access-Control-Allow-Origin: '*' allows requests from any domain
    # In production, replace '*' with your specific domain for security
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        # Handle CORS preflight request
        # Browsers send OPTIONS request before actual request to check CORS permissions
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Extract query parameters from API Gateway event
        # Example: ?category=Tools&minPrice=50
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Initialize scan parameters with table name
        scan_params = {'TableName': table_name}
        
        # Build filter expression if query parameters exist
        if query_params:
            filter_expressions = []  # List of filter conditions
            expression_attribute_values = {}  # Values for placeholders
            expression_attribute_names = {}  # Attribute name aliases
            
            # Filter by category (exact match)
            # Example: category=Machinery
            if 'category' in query_params:
                filter_expressions.append('#cat = :category')
                expression_attribute_names['#cat'] = 'category'
                expression_attribute_values[':category'] = {'S': query_params['category']}
            
            # Filter by name (partial match using contains)
            # Example: name=Drill
            if 'name' in query_params:
                filter_expressions.append('contains(#name, :name)')
                expression_attribute_names['#name'] = 'name'
                expression_attribute_values[':name'] = {'S': query_params['name']}
            
            # Filter by minimum price
            # Example: minPrice=100
            if 'minPrice' in query_params:
                filter_expressions.append('#price >= :minPrice')
                expression_attribute_names['#price'] = 'price'
                expression_attribute_values[':minPrice'] = {'N': query_params['minPrice']}
            
            # Filter by maximum price
            # Example: maxPrice=5000
            if 'maxPrice' in query_params:
                filter_expressions.append('#price <= :maxPrice')
                expression_attribute_names['#price'] = 'price'
                expression_attribute_values[':maxPrice'] = {'N': query_params['maxPrice']}
            
            # Add filter expression to scan parameters if filters exist
            if filter_expressions:
                scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
                scan_params['ExpressionAttributeValues'] = expression_attribute_values
                scan_params['ExpressionAttributeNames'] = expression_attribute_names
        
        # Execute scan operation on DynamoDB table
        response = dynamodb.scan(**scan_params)
        
        # Convert DynamoDB format to simple JSON
        # DynamoDB returns items in format: {'attribute': {'S': 'value'}} or {'attribute': {'N': '123'}}
        # We convert to: {'attribute': 'value'} or {'attribute': 123}
        items = []
        for item in response.get('Items', []):
            converted_item = {}
            for key, value in item.items():
                if 'S' in value:  # String type
                    converted_item[key] = value['S']
                elif 'N' in value:  # Number type
                    converted_item[key] = float(value['N'])
            items.append(converted_item)
        
        # Return successful response with products
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'count': len(items),
                'products': items
            })
        }
        
    except Exception as e:
        # Log error and return error response
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
