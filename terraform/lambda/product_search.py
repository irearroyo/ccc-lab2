import json
import boto3
import os
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'ProductInventory')
table = dynamodb.Table(table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

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
        
        if not query_params:
            response = table.scan()
        else:
            filter_expression = None
            
            if 'category' in query_params:
                filter_expression = Attr('category').eq(query_params['category'])
            
            if 'name' in query_params:
                name_filter = Attr('name').contains(query_params['name'])
                filter_expression = name_filter if not filter_expression else filter_expression & name_filter
            
            if 'minPrice' in query_params:
                price_filter = Attr('price').gte(Decimal(query_params['minPrice']))
                filter_expression = price_filter if not filter_expression else filter_expression & price_filter
            
            if 'maxPrice' in query_params:
                price_filter = Attr('price').lte(Decimal(query_params['maxPrice']))
                filter_expression = price_filter if not filter_expression else filter_expression & price_filter
            
            if filter_expression:
                response = table.scan(FilterExpression=filter_expression)
            else:
                response = table.scan()
        
        items = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'count': len(items),
                'products': items
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
