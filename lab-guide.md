# Cloud Computing Lab: Serverless REST API with Monitoring

## Lab Overview
Build a serverless product inventory search system using AWS services, first manually through the console, then automate with Terraform. Add monitoring to track usage and performance.

## Architecture
- **Frontend**: Static website hosted on S3
- **API Layer**: API Gateway REST API
- **Compute**: Lambda function (Python)
- **Database**: DynamoDB
- **Monitoring**: CloudWatch (metrics, logs, alarms)

## Learning Objectives
- Deploy serverless REST API architecture
- Implement Infrastructure as Code with Terraform
- Configure CloudWatch monitoring and alarms
- Understand AWS service integration

---

## Phase 1: Console Implementation (Manual Setup)

### Step 1: Create DynamoDB Table

1. Navigate to **DynamoDB Console**
2. Click **Create table**
3. Configure:
   - **Table name**: `ProductInventory`
   - **Partition key**: `productId` (String)
   - **Table settings**: Use default settings (On-demand capacity)
4. Click **Create table**

### Step 2: Add Sample Data

1. Open the `ProductInventory` table
2. Click **Explore table items** → **Create item**
3. Add these sample products (create 5-10 items):

```json
{
  "productId": "PROD001",
  "name": "Industrial Drill Press",
  "category": "Machinery",
  "price": 1250.00,
  "stock": 15,
  "manufacturer": "ToolCorp",
  "lastUpdated": "2026-01-06"
}
```

```json
{
  "productId": "PROD002",
  "name": "Safety Helmet",
  "category": "Safety Equipment",
  "price": 45.99,
  "stock": 200,
  "manufacturer": "SafetyFirst",
  "lastUpdated": "2026-01-06"
}
```

```json
{
  "productId": "PROD003",
  "name": "Hydraulic Lift",
  "category": "Machinery",
  "price": 8500.00,
  "stock": 3,
  "manufacturer": "LiftMaster",
  "lastUpdated": "2026-01-05"
}
```

### Step 3: Create Lambda Function

1. Navigate to **Lambda Console**
2. Click **Create function**
3. Configure:
   - **Function name**: `ProductSearchFunction`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
4. Click **Create function**

5. Replace the function code with:

```python
import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ProductInventory')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        # Handle OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {})
        
        if not query_params:
            # Return all products if no filter
            response = table.scan()
        else:
            # Build filter expression
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
            
            # Scan with filter
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
```

6. Click **Deploy**

### Step 4: Configure Lambda IAM Role

1. In the Lambda function, go to **Configuration** → **Permissions**
2. Click on the **Role name** (opens IAM console)
3. Click **Add permissions** → **Attach policies**
4. Search and attach: `AmazonDynamoDBReadOnlyAccess`
5. Click **Attach policy**

### Step 5: Create API Gateway

1. Navigate to **API Gateway Console**
2. Click **Create API**
3. Choose **REST API** (not private) → **Build**
4. Configure:
   - **API name**: `ProductInventoryAPI`
   - **Endpoint Type**: Regional
5. Click **Create API**

### Step 6: Configure API Resources and Methods

1. Click **Actions** → **Create Resource**
   - **Resource Name**: `products`
   - **Resource Path**: `/products`
   - Enable **CORS**
2. Click **Create Resource**

3. Select `/products` resource → **Actions** → **Create Method** → **GET**
4. Configure GET method:
   - **Integration type**: Lambda Function
   - **Lambda Function**: `ProductSearchFunction`
   - **Use Lambda Proxy integration**: ✓ (checked)
5. Click **Save** → **OK** (to grant permissions)

6. Enable CORS:
   - Select `/products` → **Actions** → **Enable CORS**
   - Keep defaults → **Enable CORS and replace existing CORS headers**
   - Confirm

### Step 7: Deploy API

1. Click **Actions** → **Deploy API**
2. Configure:
   - **Deployment stage**: [New Stage]
   - **Stage name**: `prod`
3. Click **Deploy**
4. **Copy the Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

### Step 8: Create S3 Bucket for Static Website

1. Navigate to **S3 Console**
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `product-inventory-web-[your-initials-random]` (must be globally unique)
   - **Region**: Same as your other resources
   - **Uncheck** "Block all public access"
   - Acknowledge the warning
4. Click **Create bucket**

### Step 9: Enable Static Website Hosting

1. Open your bucket → **Properties** tab
2. Scroll to **Static website hosting** → **Edit**
3. Configure:
   - **Static website hosting**: Enable
   - **Hosting type**: Host a static website
   - **Index document**: `index.html`
4. Click **Save changes**
5. **Copy the Bucket website endpoint URL**

### Step 10: Configure Bucket Policy

1. Go to **Permissions** tab
2. Scroll to **Bucket policy** → **Edit**
3. Add this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

4. Click **Save changes**

### Step 11: Create and Upload Static Website

Create `index.html` with this content (replace `YOUR-API-GATEWAY-URL`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Inventory Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .search-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .search-form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
        }
        
        input, select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
        }
        
        .btn-search:hover {
            background: #5568d3;
        }
        
        .btn-reset {
            background: #6c757d;
            color: white;
        }
        
        .btn-reset:hover {
            background: #5a6268;
        }
        
        .results-section {
            margin-top: 20px;
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .product-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .product-id {
            color: #667eea;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 10px;
        }
        
        .product-name {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .product-category {
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            margin-bottom: 10px;
        }
        
        .product-details {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .detail-label {
            color: #666;
        }
        
        .detail-value {
            font-weight: 600;
            color: #333;
        }
        
        .price {
            color: #28a745;
            font-size: 20px;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Product Inventory Search</h1>
        
        <div class="search-section">
            <form id="searchForm" class="search-form">
                <div class="form-group">
                    <label for="category">Category</label>
                    <select id="category">
                        <option value="">All Categories</option>
                        <option value="Machinery">Machinery</option>
                        <option value="Safety Equipment">Safety Equipment</option>
                        <option value="Tools">Tools</option>
                        <option value="Materials">Materials</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="name">Product Name</label>
                    <input type="text" id="name" placeholder="Search by name...">
                </div>
                
                <div class="form-group">
                    <label for="minPrice">Min Price ($)</label>
                    <input type="number" id="minPrice" placeholder="0" step="0.01">
                </div>
                
                <div class="form-group">
                    <label for="maxPrice">Max Price ($)</label>
                    <input type="number" id="maxPrice" placeholder="10000" step="0.01">
                </div>
            </form>
            
            <div class="button-group">
                <button class="btn-search" onclick="searchProducts()">🔍 Search</button>
                <button class="btn-reset" onclick="resetSearch()">🔄 Reset</button>
            </div>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
        
        <div class="results-section">
            <div class="results-header">
                <h2>Results</h2>
                <span id="resultCount">Loading...</span>
            </div>
            <div id="results" class="product-grid"></div>
        </div>
    </div>

    <script>
        const API_URL = 'YOUR-API-GATEWAY-URL/products';
        
        // Load all products on page load
        window.onload = function() {
            searchProducts();
        };
        
        async function searchProducts() {
            const resultsDiv = document.getElementById('results');
            const errorDiv = document.getElementById('error');
            const countSpan = document.getElementById('resultCount');
            
            // Hide error
            errorDiv.style.display = 'none';
            
            // Show loading
            resultsDiv.innerHTML = '<div class="loading">Loading products...</div>';
            countSpan.textContent = 'Loading...';
            
            // Build query parameters
            const params = new URLSearchParams();
            
            const category = document.getElementById('category').value;
            const name = document.getElementById('name').value;
            const minPrice = document.getElementById('minPrice').value;
            const maxPrice = document.getElementById('maxPrice').value;
            
            if (category) params.append('category', category);
            if (name) params.append('name', name);
            if (minPrice) params.append('minPrice', minPrice);
            if (maxPrice) params.append('maxPrice', maxPrice);
            
            const queryString = params.toString();
            const url = queryString ? `${API_URL}?${queryString}` : API_URL;
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch products');
                }
                
                displayResults(data.products, data.count);
                
            } catch (error) {
                console.error('Error:', error);
                errorDiv.textContent = `Error: ${error.message}`;
                errorDiv.style.display = 'block';
                resultsDiv.innerHTML = '';
                countSpan.textContent = '0 products found';
            }
        }
        
        function displayResults(products, count) {
            const resultsDiv = document.getElementById('results');
            const countSpan = document.getElementById('resultCount');
            
            countSpan.textContent = `${count} product${count !== 1 ? 's' : ''} found`;
            
            if (products.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">No products found. Try adjusting your search criteria.</div>';
                return;
            }
            
            resultsDiv.innerHTML = products.map(product => `
                <div class="product-card">
                    <div class="product-id">${product.productId}</div>
                    <div class="product-name">${product.name}</div>
                    <span class="product-category">${product.category}</span>
                    
                    <div class="product-details">
                        <div class="detail-row">
                            <span class="detail-label">Price:</span>
                            <span class="price">$${parseFloat(product.price).toFixed(2)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Stock:</span>
                            <span class="detail-value">${product.stock} units</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Manufacturer:</span>
                            <span class="detail-value">${product.manufacturer}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Last Updated:</span>
                            <span class="detail-value">${product.lastUpdated}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function resetSearch() {
            document.getElementById('searchForm').reset();
            searchProducts();
        }
        
        // Allow Enter key to trigger search
        document.getElementById('searchForm').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchProducts();
            }
        });
    </script>
</body>
</html>
```

**Important**: Replace `YOUR-API-GATEWAY-URL` with your actual API Gateway invoke URL from Step 7.

Upload to S3:
1. Go to your S3 bucket → **Objects** tab
2. Click **Upload** → **Add files**
3. Select `index.html`
4. Click **Upload**

### Step 12: Test the Application

1. Open the **S3 website endpoint URL** (from Step 9)
2. The page should load and display all products
3. Test search filters:
   - Filter by category
   - Search by name
   - Filter by price range
   - Combine multiple filters

---

## Phase 2: Add Monitoring

### Step 13: Enable CloudWatch Logs for Lambda

1. Go to **Lambda Console** → `ProductSearchFunction`
2. Go to **Configuration** → **Monitoring and operations tools**
3. Logs are automatically enabled - note the **Log group** name

### Step 14: Enable CloudWatch Logs for API Gateway

1. Go to **API Gateway Console** → `ProductInventoryAPI`
2. Select **Stages** → `prod`
3. Go to **Logs/Tracing** tab
4. Click **Edit**
5. Enable:
   - **CloudWatch Logs**: ✓
   - **Log level**: INFO
   - **Log full requests/responses data**: ✓
   - **Enable Detailed CloudWatch Metrics**: ✓
6. Click **Save changes**

### Step 15: Create CloudWatch Dashboard

1. Navigate to **CloudWatch Console**
2. Click **Dashboards** → **Create dashboard**
3. **Dashboard name**: `ProductInventoryDashboard`
4. Click **Create dashboard**

5. Add widgets:
   - Click **Add widget** → **Line**
   - Select **Metrics**
   - Choose **Lambda** → **By Function Name**
   - Select metrics for `ProductSearchFunction`:
     - `Invocations`
     - `Errors`
     - `Duration`
   - Click **Create widget**

6. Add API Gateway metrics:
   - Click **Add widget** → **Line**
   - Select **API Gateway** → **By API Name**
   - Select metrics for `ProductInventoryAPI`:
     - `Count` (requests)
     - `4XXError`
     - `5XXError`
     - `Latency`
   - Click **Create widget**

7. Click **Save dashboard**

### Step 16: Create CloudWatch Alarms

1. Go to **CloudWatch** → **Alarms** → **Create alarm**
2. Click **Select metric**
3. Choose **Lambda** → **By Function Name** → `ProductSearchFunction` → **Errors**
4. Configure:
   - **Statistic**: Sum
   - **Period**: 5 minutes
   - **Threshold**: Greater than 5
   - **Alarm name**: `ProductSearch-HighErrors`
5. Configure notification (optional - requires SNS topic)
6. Click **Create alarm**

Create another alarm for API latency:
1. **Metric**: API Gateway → `ProductInventoryAPI` → Latency
2. **Threshold**: Greater than 1000ms
3. **Alarm name**: `ProductAPI-HighLatency`

### Step 17: View Logs and Metrics

1. **Lambda Logs**:
   - Lambda Console → `ProductSearchFunction` → **Monitor** → **View CloudWatch logs**
   - Click on latest log stream to see invocation logs

2. **API Gateway Logs**:
   - CloudWatch Console → **Log groups** → `/aws/apigateway/ProductInventoryAPI`

3. **Dashboard**:
   - CloudWatch → **Dashboards** → `ProductInventoryDashboard`
   - View real-time metrics

---

## Phase 3: Terraform Implementation

Now automate everything with Infrastructure as Code!

### Step 18: Clean Up Console Resources (Optional)

Before implementing with Terraform, you can delete the console-created resources or use different names in Terraform.

### Step 19: Install Terraform

```bash
# macOS
brew install terraform

# Verify installation
terraform --version
```

### Step 20: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

### Step 21: Create Terraform Configuration Files

Create the following directory structure:
```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── lambda/
│   └── product_search.py
└── website/
    └── index.html
```

See the separate Terraform files in this repository.

### Step 22: Initialize and Apply Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Type `yes` when prompted.

### Step 23: Get Outputs

```bash
terraform output
```

Copy the `api_gateway_url` and update the `index.html` file in the `website/` directory.

### Step 24: Upload Website with Updated API URL

After updating the API URL in `index.html`, re-apply:

```bash
terraform apply
```

---

## Testing and Validation

### Test Checklist

- [ ] Website loads from S3 endpoint
- [ ] All products display on initial load
- [ ] Category filter works
- [ ] Name search works
- [ ] Price range filter works
- [ ] Combined filters work
- [ ] API returns correct JSON format
- [ ] Lambda logs appear in CloudWatch
- [ ] API Gateway logs appear in CloudWatch
- [ ] Dashboard shows metrics
- [ ] Alarms are configured

### API Testing with curl

```bash
# Get all products
curl "YOUR-API-URL/products"

# Filter by category
curl "YOUR-API-URL/products?category=Machinery"

# Search by name
curl "YOUR-API-URL/products?name=Drill"

# Price range
curl "YOUR-API-URL/products?minPrice=100&maxPrice=2000"

# Combined filters
curl "YOUR-API-URL/products?category=Machinery&maxPrice=5000"
```

---

## Monitoring Queries

### CloudWatch Insights Queries

1. Go to **CloudWatch** → **Logs Insights**
2. Select Lambda log group
3. Run queries:

**Count invocations per hour:**
```
fields @timestamp, @message
| stats count() by bin(5m)
```

**Find errors:**
```
fields @timestamp, @message
| filter @message like /Error/
| sort @timestamp desc
```

**Average duration:**
```
fields @duration
| stats avg(@duration), max(@duration), min(@duration)
```

---

## Cost Estimation

For this lab (assuming light usage):
- **DynamoDB**: Free tier (25 GB storage, 25 WCU, 25 RCU)
- **Lambda**: Free tier (1M requests/month)
- **API Gateway**: Free tier (1M requests/month for 12 months)
- **S3**: ~$0.023/GB/month + minimal request costs
- **CloudWatch**: Free tier (10 custom metrics, 5GB logs)

**Estimated monthly cost**: $0-2 for light usage

---

## Cleanup

### Console Cleanup
1. Delete S3 bucket (empty first)
2. Delete API Gateway API
3. Delete Lambda function
4. Delete DynamoDB table
5. Delete CloudWatch alarms and dashboard
6. Delete IAM roles (if not used elsewhere)

### Terraform Cleanup
```bash
cd terraform
terraform destroy
```

Type `yes` when prompted.

---

## Learning Assessment Questions

1. What are the advantages of serverless architecture?
2. How does API Gateway integrate with Lambda?
3. Why use DynamoDB instead of RDS for this use case?
4. What metrics are most important for monitoring this application?
5. How would you implement authentication for this API?
6. What are the benefits of Infrastructure as Code?
7. How would you implement CI/CD for this application?
8. What would you change to handle millions of requests?

---

## Extensions (Optional Challenges)

1. **Add POST endpoint** to create new products
2. **Implement pagination** for large result sets
3. **Add CloudFront** distribution for S3 website
4. **Implement API key authentication**
5. **Add X-Ray tracing** for distributed tracing
6. **Create SNS notifications** for alarms
7. **Implement DynamoDB Streams** to track changes
8. **Add ElastiCache** for caching frequent queries
9. **Implement WAF** for API security
10. **Add automated testing** with pytest

---

## Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

---

## Support

For issues or questions:
1. Check CloudWatch logs for errors
2. Verify IAM permissions
3. Confirm CORS configuration
4. Test API with curl before testing website
5. Check security group and network settings

Good luck with your lab! 🚀
