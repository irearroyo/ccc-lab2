import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.client('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'ProductInventory')

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Build scan parameters
        scan_params = {'TableName': table_name}
        
        if query_params:
            filter_expressions = []
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            if 'category' in query_params:
                filter_expressions.append('#cat = :category')
                expression_attribute_names['#cat'] = 'category'
                expression_attribute_values[':category'] = {'S': query_params['category']}
            
            if 'name' in query_params:
                filter_expressions.append('contains(#name, :name)')
                expression_attribute_names['#name'] = 'name'
                expression_attribute_values[':name'] = {'S': query_params['name']}
            
            if 'minPrice' in query_params:
                filter_expressions.append('#price >= :minPrice')
                expression_attribute_names['#price'] = 'price'
                expression_attribute_values[':minPrice'] = {'N': query_params['minPrice']}
            
            if 'maxPrice' in query_params:
                filter_expressions.append('#price <= :maxPrice')
                expression_attribute_names['#price'] = 'price'
                expression_attribute_values[':maxPrice'] = {'N': query_params['maxPrice']}
            
            if filter_expressions:
                scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
                scan_params['ExpressionAttributeValues'] = expression_attribute_values
                scan_params['ExpressionAttributeNames'] = expression_attribute_names
        
        # Execute scan
        response = dynamodb.scan(**scan_params)
        
        # Convert DynamoDB format to simple JSON
        items = []
        for item in response.get('Items', []):
            converted_item = {}
            for key, value in item.items():
                if 'S' in value:
                    converted_item[key] = value['S']
                elif 'N' in value:
                    converted_item[key] = float(value['N'])
            items.append(converted_item)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'count': len(items),
                'products': items
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
