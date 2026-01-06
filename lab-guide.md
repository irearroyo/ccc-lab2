# Cloud Computing Lab: Serverless REST API with Monitoring

## Lab Overview
Build a serverless product inventory search system using AWS services, first manually through the console, then automate with Terraform. Add monitoring to track usage and performance.

## Architecture
- **CDN**: CloudFront distribution for global content delivery
- **Frontend**: Static website hosted on S3
- **Security**: WAF (Web Application Firewall) for API protection
- **Network**: VPC with private subnets for Lambda
- **API Layer**: API Gateway REST API
- **Compute**: Lambda function (Python) in VPC
- **Database**: DynamoDB (accessed via VPC endpoint)
- **Monitoring**: CloudWatch (metrics, logs, alarms)
- **Notifications**: SNS for alerts and notifications

## Learning Objectives
- Deploy production-grade serverless REST API architecture
- Implement Infrastructure as Code with Terraform
- Configure CloudWatch monitoring and alarms
- Secure APIs with WAF rules
- Distribute content globally with CloudFront
- Set up automated notifications with SNS
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

### Step 3: Create VPC and Subnets

**Why VPC?** Placing Lambda in a VPC provides network isolation and allows private communication with AWS services.

1. Navigate to **VPC Console**
2. Click **Create VPC**
3. Configure:
   - **Resources to create**: VPC and more
   - **Name tag**: `ProductInventory-VPC`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Number of Availability Zones**: 2
   - **Number of public subnets**: 2
   - **Number of private subnets**: 2
   - **NAT gateways**: None (we'll use VPC endpoints instead)
   - **VPC endpoints**: S3 Gateway
4. Click **Create VPC**

**Note the following IDs** (you'll need them later):
- VPC ID
- Private Subnet IDs (2 subnets)
- Security Group ID (default)

### Step 4: Create VPC Endpoint for DynamoDB

**Why VPC Endpoint?** Allows Lambda to access DynamoDB without needing internet access or NAT Gateway (saves cost).

1. In **VPC Console**, go to **Endpoints**
2. Click **Create endpoint**
3. Configure:
   - **Name**: `ProductInventory-DynamoDB-Endpoint`
   - **Service category**: AWS services
   - **Service name**: Search for `dynamodb` → Select `com.amazonaws.[region].dynamodb` (Gateway type)
   - **VPC**: Select `ProductInventory-VPC`
   - **Route tables**: Select all route tables associated with your private subnets
   - **Policy**: Full access
4. Click **Create endpoint**

### Step 5: Create Security Group for Lambda

1. In **VPC Console**, go to **Security Groups**
2. Click **Create security group**
3. Configure:
   - **Name**: `ProductInventory-Lambda-SG`
   - **Description**: Security group for Lambda function
   - **VPC**: Select `ProductInventory-VPC`
4. **Outbound rules**:
   - Keep default (All traffic to 0.0.0.0/0)
   - This allows Lambda to call DynamoDB via VPC endpoint
5. **Inbound rules**: None needed (Lambda doesn't receive inbound traffic)
6. Click **Create security group**
7. **Copy the Security Group ID**

### Step 6: Create Lambda Function

1. Navigate to **Lambda Console**
2. Click **Create function**
3. Configure:
   - **Function name**: `ProductSearchFunction`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
   - **Advanced settings** → Expand
   - **Enable VPC**: ✓ (checked)
   - **VPC**: Select `ProductInventory-VPC`
   - **Subnets**: Select both **private subnets**
   - **Security groups**: Select `ProductInventory-Lambda-SG`
4. Click **Create function**

**Note**: Lambda in VPC takes longer to cold start (~10-15 seconds first time)

5. **Wait 1-2 minutes** for VPC configuration to complete

6. Replace the function code with:

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

7. Click **Deploy**

### Step 7: Configure Lambda IAM Role

**Lambda in VPC needs additional permissions** to create network interfaces.

1. In the Lambda function, go to **Configuration** → **Permissions**
2. Click on the **Role name** (opens IAM console)
3. Click **Add permissions** → **Attach policies**
4. Search and attach these policies:
   - `AmazonDynamoDBReadOnlyAccess` (for DynamoDB access)
   - `AWSLambdaVPCAccessExecutionRole` (for VPC network interfaces)
5. Click **Attach policies**

**Verify permissions**: The role should now have:
- AmazonDynamoDBReadOnlyAccess
- AWSLambdaVPCAccessExecutionRole
- AWSLambdaBasicExecutionRole (auto-created)

### Step 8: Test Lambda in VPC

1. Go back to Lambda function
2. Click **Test** tab
3. Create a test event:
```json
{
  "httpMethod": "GET",
  "queryStringParameters": null
}
```
4. Click **Test**
5. Should return products successfully (may take 10-15 seconds on first run due to VPC cold start)

**If it fails**: Check that VPC endpoint for DynamoDB is created and associated with the correct route tables.

### Step 9: Create API Gateway

1. Navigate to **API Gateway Console**
2. Click **Create API**
3. Choose **REST API** (not private) → **Build**
4. Configure:
   - **API name**: `ProductInventoryAPI`
   - **Endpoint Type**: Regional
5. Click **Create API**

### Step 10: Configure API Resources and Methods

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

### Step 11: Deploy API

1. Click **Actions** → **Deploy API**
2. Configure:
   - **Deployment stage**: [New Stage]
   - **Stage name**: `prod`
3. Click **Deploy**
4. **Copy the Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

### Step 12: Create S3 Bucket for Static Website

1. Navigate to **S3 Console**
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `product-inventory-web-[your-initials-random]` (must be globally unique)
   - **Region**: Same as your other resources
   - **Uncheck** "Block all public access"
   - Acknowledge the warning
4. Click **Create bucket**

### Step 13: Enable Static Website Hosting

1. Open your bucket → **Properties** tab
2. Scroll to **Static website hosting** → **Edit**
3. Configure:
   - **Static website hosting**: Enable
   - **Hosting type**: Host a static website
   - **Index document**: `index.html`
4. Click **Save changes**
5. **Copy the Bucket website endpoint URL**

### Step 14: Configure Bucket Policy

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

### Step 15: Create and Upload Static Website

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

### Step 16: Create SNS Topic for Notifications

1. Navigate to **SNS Console**
2. Click **Topics** → **Create topic**
3. Configure:
   - **Type**: Standard
   - **Name**: `ProductInventoryAlerts`
   - **Display name**: `Product Alerts`
4. Click **Create topic**
5. **Copy the Topic ARN**

### Step 17: Create SNS Subscription

1. In the topic details, click **Create subscription**
2. Configure:
   - **Protocol**: Email
   - **Endpoint**: Your email address
3. Click **Create subscription**
4. **Check your email** and click the confirmation link
5. Status should change to "Confirmed"

### Step 18: Create CloudFront Distribution

1. Navigate to **CloudFront Console**
2. Click **Create distribution**
3. Configure **Origin**:
   - **Origin domain**: Select your S3 bucket website endpoint (use the format: `bucket-name.s3-website-region.amazonaws.com`)
   - **Protocol**: HTTP only (for S3 website endpoint)
   - **Name**: Leave default
4. Configure **Default cache behavior**:
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Allowed HTTP methods**: GET, HEAD, OPTIONS
   - **Cache policy**: CachingOptimized
5. Configure **Settings**:
   - **Price class**: Use all edge locations (best performance)
   - **Alternate domain name (CNAME)**: Leave empty (or add your custom domain)
   - **Default root object**: `index.html`
6. Click **Create distribution**
7. **Wait 5-10 minutes** for deployment (Status: "Enabled")
8. **Copy the Distribution domain name** (e.g., `d1234abcd.cloudfront.net`)

**Note**: You'll need to update the website to use the CloudFront URL instead of direct S3 access.

### Step 19: Create WAF Web ACL

1. Navigate to **WAF & Shield Console**
2. Click **Web ACLs** → **Create web ACL**
3. Configure **Web ACL details**:
   - **Name**: `ProductInventoryWAF`
   - **Resource type**: Regional resources (API Gateway)
   - **Region**: Same as your API Gateway
4. Click **Next**

5. **Add AWS managed rule groups**:
   - Click **Add rules** → **Add managed rule groups**
   - Expand **AWS managed rule groups**
   - Enable these rule groups:
     - ✓ **Core rule set** (protects against common threats)
     - ✓ **Known bad inputs** (blocks malicious patterns)
     - ✓ **SQL database** (SQL injection protection)
   - Click **Add rules**
6. Click **Next**

7. **Set rule priority**: Keep default order
8. Click **Next**

9. **Configure metrics**: Keep defaults
10. Click **Next**

11. **Review and create**: Click **Create web ACL**

### Step 20: Associate WAF with API Gateway

1. In the WAF Web ACL details, go to **Associated AWS resources**
2. Click **Add AWS resources**
3. Select **API Gateway**
4. Choose your `ProductInventoryAPI` → stage `prod`
5. Click **Add**

**Note**: WAF will now protect your API from common attacks.

### Step 21: Update Website to Use CloudFront

1. Go to your S3 bucket
2. Download the `index.html` file
3. Update the API URL to use your API Gateway URL (keep this the same)
4. Re-upload the file to S3
5. **Invalidate CloudFront cache**:
   - Go to CloudFront Console → Your distribution
   - Go to **Invalidations** tab
   - Click **Create invalidation**
   - Enter `/*` (invalidate all files)
   - Click **Create invalidation**

### Step 22: Test the Application

1. Open the **CloudFront distribution URL** (from Step 14)
2. The page should load and display all products
3. Test search filters:
   - Filter by category
   - Search by name
   - Filter by price range
   - Combine multiple filters
4. **Test from different locations** to see CloudFront caching in action

**Performance Comparison**:
- Direct S3: ~200-500ms (depending on location)
- CloudFront: ~50-100ms (cached at edge locations)

---

## Phase 2: Add Monitoring

### Step 23: Enable CloudWatch Logs for Lambda

1. Go to **Lambda Console** → `ProductSearchFunction`
2. Go to **Configuration** → **Monitoring and operations tools**
3. Logs are automatically enabled - note the **Log group** name

### Step 24: Enable CloudWatch Logs for API Gateway

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

### Step 25: Create CloudWatch Dashboard

1. Navigate to **CloudWatch Console**
2. Click **Dashboards** → **Create dashboard**
3. **Dashboard name**: `ProductInventoryDashboard`
4. Click **Create dashboard**

5. **Add Lambda metrics widget**:
   - Click **Add widget** → **Line**
   - Select **Metrics**
   - Choose **Lambda** → **By Function Name**
   - Select metrics for `ProductSearchFunction`:
     - `Invocations`
     - `Errors`
     - `Duration`
   - Click **Create widget**

6. **Add API Gateway metrics widget**:
   - Click **Add widget** → **Line**
   - Select **API Gateway** → **By API Name**
   - Select metrics for `ProductInventoryAPI`:
     - `Count` (requests)
     - `4XXError`
     - `5XXError`
     - `Latency`
   - Click **Create widget**

7. **Add CloudFront metrics widget**:
   - Click **Add widget** → **Line**
   - Select **CloudFront** → **Per-Distribution Metrics**
   - Select your distribution and metrics:
     - `Requests`
     - `BytesDownloaded`
     - `4xxErrorRate`
     - `5xxErrorRate`
   - Click **Create widget**

8. **Add WAF metrics widget**:
   - Click **Add widget** → **Line**
   - Select **WAF** → **By WebACL**
   - Select your Web ACL and metrics:
     - `AllowedRequests`
     - `BlockedRequests`
     - `CountedRequests`
   - Click **Create widget**

9. Click **Save dashboard**

### Step 26: Create CloudWatch Alarms with SNS Notifications

**Alarm 1: Lambda Errors**

1. Go to **CloudWatch** → **Alarms** → **Create alarm**
2. Click **Select metric**
3. Choose **Lambda** → **By Function Name** → `ProductSearchFunction` → **Errors**
4. Configure metric:
   - **Statistic**: Sum
   - **Period**: 5 minutes
5. Configure conditions:
   - **Threshold type**: Static
   - **Whenever Errors is**: Greater than `5`
6. Configure actions:
   - **Alarm state trigger**: In alarm
   - **Select an SNS topic**: Select existing `ProductInventoryAlerts`
7. Configure name:
   - **Alarm name**: `ProductSearch-HighErrors`
   - **Description**: Alert when Lambda errors exceed 5 in 5 minutes
8. Click **Create alarm**

**Alarm 2: API Latency**

1. Create another alarm
2. **Metric**: API Gateway → `ProductInventoryAPI` → Latency
3. **Statistic**: Average
4. **Period**: 5 minutes
5. **Threshold**: Greater than `1000` (ms)
6. **SNS topic**: `ProductInventoryAlerts`
7. **Alarm name**: `ProductAPI-HighLatency`
8. Click **Create alarm**

**Alarm 3: WAF Blocked Requests**

1. Create another alarm
2. **Metric**: WAF → By WebACL → `ProductInventoryWAF` → BlockedRequests
3. **Statistic**: Sum
4. **Period**: 5 minutes
5. **Threshold**: Greater than `10`
6. **SNS topic**: `ProductInventoryAlerts`
7. **Alarm name**: `WAF-HighBlockedRequests`
8. **Description**: Alert when WAF blocks more than 10 requests
9. Click **Create alarm**

**Alarm 4: CloudFront 5xx Errors**

1. Create another alarm
2. **Metric**: CloudFront → Per-Distribution → Your distribution → 5xxErrorRate
3. **Statistic**: Average
4. **Period**: 5 minutes
5. **Threshold**: Greater than `1` (%)
6. **SNS topic**: `ProductInventoryAlerts`
7. **Alarm name**: `CloudFront-High5xxErrors`
8. Click **Create alarm**

**Test Notifications**:
- You should receive email notifications when alarms trigger
- Check your email inbox for SNS notifications

### Step 27: View Logs and Metrics

1. **Lambda Logs**:
   - Lambda Console → `ProductSearchFunction` → **Monitor** → **View CloudWatch logs**
   - Click on latest log stream to see invocation logs

2. **API Gateway Logs**:
   - CloudWatch Console → **Log groups** → `/aws/apigateway/ProductInventoryAPI`

3. **WAF Logs** (Optional - requires S3 or Kinesis):
   - WAF Console → Your Web ACL → **Logging and metrics**
   - Enable logging to see blocked requests

4. **CloudFront Logs** (Optional):
   - CloudFront Console → Your distribution → **Logs**
   - Enable standard logging to S3

5. **Dashboard**:
   - CloudWatch → **Dashboards** → `ProductInventoryDashboard`
   - View real-time metrics for all services

### Step 28: Test WAF Protection

Test that WAF is blocking malicious requests:

```bash
# Normal request (should work)
curl "YOUR-API-URL/products"

# SQL injection attempt (should be blocked by WAF)
curl "YOUR-API-URL/products?category=Machinery' OR '1'='1"

# XSS attempt (should be blocked by WAF)
curl "YOUR-API-URL/products?name=<script>alert('xss')</script>"
```

Check WAF metrics in CloudWatch to see blocked requests.

---

## Phase 3: Terraform Implementation

Now automate everything with Infrastructure as Code!

### Step 29: Verify VPC Configuration

Let's verify that Lambda is properly configured in the VPC:

1. Go to **Lambda Console** → `ProductSearchFunction`
2. Go to **Configuration** → **VPC**
3. Verify:
   - VPC: `ProductInventory-VPC`
   - Subnets: 2 private subnets
   - Security groups: `ProductInventory-Lambda-SG`

4. Go to **VPC Console** → **Endpoints**
5. Verify DynamoDB endpoint is **Available**

6. Test the complete flow:
   - Open CloudFront URL
   - Search for products
   - Check Lambda logs for successful execution
   - Verify no internet gateway is used (all traffic via VPC endpoint)

**Benefits of VPC Configuration**:
- ✅ Network isolation and security
- ✅ Private communication with DynamoDB
- ✅ No data traverses the public internet
- ✅ Compliance with security requirements
- ✅ No NAT Gateway costs (using VPC endpoints)

---

## Phase 3: Terraform Implementation

### Step 30: Clean Up Console Resources (Optional)

Before implementing with Terraform, you can delete the console-created resources or use different names in Terraform.

### Step 31: Install Terraform

```bash
# macOS
brew install terraform

# Verify installation
terraform --version
```

### Step 32: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

### Step 33: Create Terraform Configuration Files

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

### Step 34: Initialize and Apply Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Type `yes` when prompted.

### Step 35: Get Outputs

```bash
terraform output
```

Copy the `api_gateway_url` and update the `index.html` file in the `website/` directory.

### Step 36: Upload Website with Updated API URL

After updating the API URL in `index.html`, re-apply:

```bash
terraform apply
```

---

## Testing and Validation

### Test Checklist

- [ ] Website loads from CloudFront URL
- [ ] All products display on initial load
- [ ] Category filter works
- [ ] Name search works
- [ ] Price range filter works
- [ ] Combined filters work
- [ ] API returns correct JSON format
- [ ] Lambda logs appear in CloudWatch
- [ ] API Gateway logs appear in CloudWatch
- [ ] CloudFront caches content properly
- [ ] WAF blocks malicious requests
- [ ] Dashboard shows metrics for all services
- [ ] Alarms are configured with SNS notifications
- [ ] Email notifications work when alarms trigger

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
- **CloudFront**: Free tier (1TB data transfer out, 10M requests/month for 12 months)
- **WAF**: ~$5/month (Web ACL) + $1 per million requests
- **SNS**: Free tier (1,000 email notifications/month)
- **CloudWatch**: Free tier (10 custom metrics, 5GB logs)
- **VPC**: Free (VPC, subnets, security groups, route tables)
- **VPC Endpoints**: Free for Gateway endpoints (S3, DynamoDB)

**Estimated monthly cost**: $5-10 for light usage (mainly WAF costs)

**Cost Savings with VPC**:
- ✅ No NAT Gateway needed (~$32/month saved)
- ✅ Using Gateway endpoints (free) instead of Interface endpoints (~$7/month saved)
- ✅ No data transfer charges for DynamoDB access

**Note**: WAF is the main cost driver. For educational purposes, you can disable WAF after testing to reduce costs to ~$0-2/month.

---

## Cleanup

### Console Cleanup
1. Delete CloudFront distribution (disable first, then delete after ~15 minutes)
2. Delete WAF Web ACL (disassociate from API Gateway first)
3. Delete SNS topic and subscriptions
4. Delete S3 bucket (empty first)
5. Delete API Gateway API
6. Delete Lambda function (this will remove ENIs from VPC automatically)
7. Delete DynamoDB table
8. Delete CloudWatch alarms and dashboard
9. Delete VPC endpoints (DynamoDB and S3)
10. Delete VPC (this will delete subnets, route tables, and security groups)
11. Delete IAM roles (if not used elsewhere)

**Important Notes**:
- CloudFront distributions take 15+ minutes to delete
- Lambda ENIs (Elastic Network Interfaces) are automatically deleted when Lambda is deleted
- VPC can only be deleted after all resources using it are removed
- Delete in the order listed above to avoid dependency errors

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
3. **Add custom domain** to CloudFront with SSL certificate
4. **Implement API key authentication**
5. **Add X-Ray tracing** for distributed tracing
6. **Enable WAF logging** to S3 for security analysis
7. **Implement DynamoDB Streams** to track changes
8. **Add ElastiCache** for caching frequent queries
9. **Add rate limiting** with WAF rate-based rules
10. **Add automated testing** with pytest
11. **Implement geo-blocking** with CloudFront
12. **Add Lambda@Edge** for custom headers

---

## Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [WAF Documentation](https://docs.aws.amazon.com/waf/)
- [SNS Documentation](https://docs.aws.amazon.com/sns/)
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
