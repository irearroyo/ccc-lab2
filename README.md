# Lab 2: Build a serverless REST API with Monitoring


## 1. Overview and Objectives

This lab guides you through building a serverless REST API to cosume data from a DynamoDB to get product inventory. You'll start by manually creating the infrastructure in the AWS Console to understand each component, then automate the entire deployment using Terraform to learn infrastructure-as-code best practices.

**Team Structure:**
- Work individually

**Learning Objectives:**
- Continue gaining hands-on understanding of AWS
- Understand API gateway fundamental
- Configure a serverless and secure Lambda function
- Create a DynamoDB table
- Understand WAF basic configuration
- Set up automated notifications with SNS
- Implement infrastructure-as-code using Terraform

## 2. Prerequisites

Before starting this lab, ensure you have the following installed and configured:

- **AWS Academy Learner Lab access**: Accept the invitation to AWS Academy and read `Academy Learner Lab Student Guide` (pages 3-7) and watch the video `Demo - How to Access Learner Lab`
- **WSL (Windows only)**: If you're on Windows, install Windows Subsystem for Linux (WSL) and use a Linux distribution (Ubuntu recommended)
- **Git**: Install Git and configure it with your name and email
- **GitHub Account**: Set up SSH authentication to be able to clone and push changes
- **Docker Desktop**: Install Docker Desktop for container support
- **Terraform**: Install Terraform (version 1.14 or later)
- **Visual Studio Code**: Install VS Code with recommended extensions:
  - Git Graph
  - Dev Containers
  - Python

## 3. Introduction

This lab is divided into two main parts:

**Part 1: Manual Configuration**: You will manually configure AWS resources through the AWS Console to understand the underlying concepts.

**Part 2: Infrastructure as Code**: You will recreate your infrastructure from the previous steps using Terraform.

The architecture diagram below shows the final API layout used in this lab:

![Final Architecture](img/final-architecture.png)

- **CDN**: CloudFront distribution for global content delivery
- **Frontend**: Static website hosted on S3
- **Security**: WAF (Web Application Firewall) for API protection
- **Network**: VPC with private subnets for Lambda
- **API Layer**: API Gateway REST API
- **Compute**: Lambda function (Python) in VPC
- **Database**: DynamoDB (accessed via VPC endpoint)
- **Monitoring**: CloudWatch (metrics, logs, alarms)
- **Notifications**: SNS for alerts and notifications

## 4. Accessing Your AWS Account

For this course, we use **AWS Academy Learner Lab** to provide access to real AWS accounts. These accounts have some limitations on available services and IAM roles to control costs, but include everything needed for this lab.

To access your AWS environment:

1. Go to **Modules** in your AWS Academy course and open **Launch AWS Academy Learner Lab**.
2. Click **Start Lab** to initialize your AWS session (the indicator will turn green when ready).
3. Click **AWS** to open the AWS Management Console in a new tab.

Make sure to keep an eye on remaining budget ($50), and avoid pressing the `Reset` button as you will lose all progress!

## Part 1: Manual Configuration


### 1: Create DynamoDB Table

DynamoDB serves as the data store for your REST API, providing fast, scalable NoSQL storage for product information that your Lambda function queries.

1. Navigate to **DynamoDB Console**
2. Click **Create table**

![Create DynamoDB table](img/step1_1.png)

3. Configure:
   - **Table name**: `ProductInventory`
   - **Partition key**: `productId` (String)
   - **Table settings**: Use default settings (On-demand capacity)
4. Click **Create table**
![Created DynamoDB table](img/step1_2.png)


### 2: Add Sample Data

1. Open the `ProductInventory` table
2. Click **Explore table items** → **Create item**

![Explore table](img/step2_1.png)

![Create item](img/step2_2.png)
3. Add these sample products from `initial_data/sample-data.json' (create 5-10 items): 
![Add item](img/step2_3.png)

```json
{
    "productId": {"S": "PROD001"},
    "name": {"S": "Industrial Drill Press"},
    "category": {"S": "Machinery"},
    "price": {"N": "1250.00"},
    "stock": {"N": "15"},
    "manufacturer": {"S": "ToolCorp"},
    "lastUpdated": {"S": "2026-01-06"}
  }
```
4. You can test to Query the data with different filters in Explore items


### Step 3: Create VPC and Subnets

**Why VPC?** Placing Lambda in a VPC provides network isolation and allows private communication with AWS services.

1. Navigate to **VPC Console**
2. Click **Create VPC**
3. Configure:

In the creation form, provide the basic settings for this lab. Typical values used in the lab are:

  - **Name tag**: Choose a name as `ProductInventory`
  - **IPv4 CIDR block**: Choose a /24 CIDR, and ensure this does not overlap with your partner's VPC!
  - **IPv6 CIDR block**: None (IPv6 adoption is growing, but IPv4 is still the main system.)
  - **Tenancy**: Default (only customers that have strict physical isolation requirements change this)
  - **Number of AZs**: 1 (note that typically for high availability you would choose at least 2)
  - **Number of Public Subnets**: 1 (will be used for a Lambda with public IPs)
  - **Number of Private Subnets**: 0 (for this lab we won't be using them. However, for security reasons Lambda would typically go in private subnets.)
  - **NAT GWs**:  None (we'll use VPC endpoints instead for accesing DynamoDB table)

![VPC](img/step3_1.png)


4. Click **Create VPC**

**Note the following IDs** (you'll need them later):
- VPC ID
- Private Subnet IDs (1 subnets)
- Security Group ID (default)

### Step 4: Create VPC Endpoint for DynamoDB

**Why VPC Endpoint?** Allows Lambda to access DynamoDB without needing internet access or NAT Gateway (saves cost).

1. In **VPC Console**, go to **Endpoints**
2. Click **Create endpoint**

![VPC Endpoint](img/step4_0.png)

3. Configure:
   - **Name**: `ProductInventory-DynamoDB-Endpoint`
   - **Service category**: AWS services
   - **Service name**: Search for `dynamodb` → Select `com.amazonaws.[region].dynamodb` (Gateway type)
   - **VPC**: Select `ProductInventory-VPC`
   - **Route tables**: Select all route tables associated with your private subnets
   - **Policy**: Full access
4. Click **Create endpoint**

![VPC Endpoint](img/step4_1.png)

![VPC Endpoint](img/step4_2.png)

### Step 5: Create Lambda Function

Lambda funcion execute serverless code to query the DynamoDB table and returns product data based on search filters like category, name, and price range.

1. Navigate to **Lambda Console**
2. Click **Create function**
3. Configure:
   - **Function name**: `ProductSearchFunction`
   - **Runtime**: Python 3.14
   - **Architecture**: x86_64
   - **Change default execution rol**: Use a existing Role -> LabRole
   - **Advanced settings** → Expand
   - **Enable VPC**: ✓ (checked)
   - **VPC**: Select `ProductInventory-VPC`
   - **Subnets**: Select the previous subnet created
   - **Security groups**: Select `default`
4. Click **Create function**

![Lambda 1](img/step5_1.png)

![Lambda 2](img/step5_2.png)

6. Replace the function code with from 'initial_data/lambda_function.py' and press "deploy"

![Lambda 3](img/step5_3.png)

7. Once it is deployed, press 'Test' to test that the lambda can query the data from DynamoDB

![Lambda 3](img/step5_4.png)

![Lambda 3](img/step5_5.png)

Test 1: Get All Products (without filters)
```json
{
  "httpMethod": "GET",
  "queryStringParameters": null,
  "headers": {
    "Content-Type": "application/json"
  }
}
```

Test 2: Filter by Category

```json
{
  "httpMethod": "GET",
  "queryStringParameters": {
    "category": "Machinery"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

![Lambda 3](img/step5_6.png)


### Step 6: Create API Gateway

1. Navigate to **API Gateway Console**
2. Click **Create API**
3. Choose **REST API** (not private) → **Build**
4. Configure:
   - **API name**: `ProductInventoryAPI`
   - **Endpoint Type**: Regional
5. Click **Create API**

![API ](img/step6.png)

### Step 7: Configure API Resources and Methods

1. Click **Actions** → **Create Resource**
   - **Resource Name**: `products`
   - **Resource Path**: `/products`
   - Enable **CORS**
2. Click **Create Resource**

![API ](img/step7.png)

3. Select `/products` resource → **Actions** → **Create Method** → **GET**

![API ](img/step7_1.png)

4. Configure GET method:
   - **Integration type**: Lambda Function
   - **Lambda Function**: `ProductSearchFunction`
   - **Use Lambda Proxy integration**: ✓ (checked)
5. Click **Save** → **OK** (to grant permissions)

![API ](img/step7_2.png)


6. Enable CORS:
  - Select `/products` → **Actions** → **Enable CORS**
  - **Gateway responses**: Keep both checkboxes selected (Default 4XX and Default 5XX)
    - This ensures error responses also include CORS headers
  - **Access-Control-Allow-Methods**: Keep **GET** checked
  - **Access-Control-Allow-Headers**: Keep the default headers
  - **Access-Control-Allow-Origin**: Keep `*` (allows all domains)
  - Click **Save**

![API ](img/step7_3.png)

### Step 8: Deploy API

1. Click **Actions** → **Deploy API**
2. Configure:
   - **Deployment stage**: [New Stage]
   - **Stage name**: `prod`
3. Click **Deploy**
4. **Copy the Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

### Step 9: Create S3 Bucket for Static Website

1. Navigate to **S3 Console**
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `product-inventory-web-us-east-1-[your-initials-random]` (must be globally unique)
   - **Region**: Same as your other resources
   - **Uncheck** "Block all public access"
   - Acknowledge the warning
4. Click **Create bucket**

### Step 10: Enable Static Website Hosting

1. Open your bucket → **Properties** tab
![Enable Static Website Hosting](img/step9_1.png)
![Enable Static Website Hosting](img/step9_2.png)
2. Scroll to **Static website hosting** → **Edit**
3. Configure:
   - **Static website hosting**: Enable
   - **Hosting type**: Host a static website
   - **Index document**: `index.html`
4. Click **Save changes**

![Enable Static Website Hosting](img/step9_3.png)

5. **Copy the Bucket website endpoint URL**



### Step 15: Create and Upload Static Website

Create `index.html` with the content from 'initial_data/index.html' content (IMPORTANT: replace `YOUR-API-GATEWAY-URL`):



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


**Important**: After deployment:
1. Check your email and confirm SNS subscription
2. Copy the CloudFront URL to access the website
3. The API Gateway URL is already configured in the website

### Testing

Run the test script:
```bash
./test-api.sh <API_GATEWAY_URL>
```

Or test manually:
```bash
# Get all products
curl "https://your-api-url/products"

# Filter by category
curl "https://your-api-url/products?category=Machinery"

# Search by name
curl "https://your-api-url/products?name=Drill"

# Price range


## Final Flow


```
┌─────────┐      ┌─────────────┐      ┌──────────────┐      ┌────────┐      ┌──────────┐
│  User   │─────▶│  S3 Static  │─────▶│ API Gateway  │─────▶│ Lambda │─────▶│ DynamoDB │
│ Browser │      │   Website   │      │  (REST API)  │      │Function│      │  Table   │
└─────────┘      └─────────────┘      └──────────────┘      └────────┘      └──────────┘
                                              │                    │
                                              │                    │
                                              ▼                    ▼
                                       ┌──────────────────────────────┐
                                       │   CloudWatch Logs & Metrics  │
                                       └──────────────────────────────┘
```
## Part 2: Infrastructure as Code

In this section, you will recreate your infrastructure using Terraform, learning infrastructure-as-code principles. Terraform allows you to define your infrastructure in code, making it reproducible, version-controlled, and easier to manage.

### 1. Bootstrap Your Git Repository

Clone this repository to your local machine. In the `/infra` folder you will find the starting point for deploying your solution in Terraform:

```
infra/
├── main.tf        # Main resource definitions (VPC already provided)
├── providers.tf   # Terraform and AWS provider configuration
├── variables.tf   # Input variable definitions
└── outputs.tf     # Output value definitions
```

The VPC resource is already defined in `main.tf` as a starting point. You will extend this to include the remaining resources.
You should be able to automatically configure the Web Server on start up using Terraform, as well as create the VPC Peering Connection.

### 2. Set Up State Bucket for Terraform

Terraform tracks all resources it creates in a **state file**. This file maps your configuration to real AWS resources, so Terraform knows what exists and what needs to change. By default, state is stored locally, but this breaks when multiple team members work on the same infrastructure—each person would have a different view of what exists. Storing state remotely in S3 ensures everyone shares the same source of truth.

We will use an S3 bucket created via CloudFormation, which is another IaC language.

1. **Go to CloudFormation in the AWS Console**
   - Search for "CloudFormation" and click **Create stack** → **With new resources (standard)**.


2. **Upload the template**
   - Select **Upload a template file** and upload the `scripts/tf-state.yaml` file from this repository.
   - This template creates an S3 bucket named `tf-state-<account-id>-<region>` to store your Terraform state.


3. **Create the stack**
   - Give the stack a name (e.g., `tf-state`).
   - Leave all other settings as default and click through to create the stack.
   - Wait for the stack status to show **CREATE_COMPLETE**.



### 3. Configure Terraform Backend

Update the `infra/providers.tf` file to reference your state bucket. Replace the bucket name with your own (using your AWS account ID):

```hcl
terraform {
  backend "s3" {
    bucket       = "tf-state-<your-account-id>-us-east-1"
    key          = "lab2/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
```

### 4. Develop Your Solution Using Terraform

Now you will replicate the infrastructure you created manually in Part 1 using Terraform.

1. **Configure AWS credentials**
   - In AWS Academy, click on **AWS Details** to open the credentials panel.
   - Click **Show** next to **AWS CLI** to reveal your temporary credentials.
   - Copy the credentials and paste them into your `~/.aws/credentials` file.


   > **Note:** These credentials are temporary and expire when your lab session ends. You will need to update them each time you start a new session.

2. **Initialize Terraform**

   The `init` command downloads the AWS provider plugin and configures the S3 backend. This must be run before any other Terraform commands and whenever you change the backend configuration.

   ```bash
   cd infra
   terraform init
   ```


3. **Modify `terraform.tfvars` file** with your project-specific values. Remember that the CIDR range should not overlap with your partner team.

4. **Plan and apply your changes**

   The `plan` command shows what Terraform will do without making changes—always review this before applying. The `apply` command executes the plan and creates real resources in AWS.

   The bootstrap code contains an empty VPC that can be deployed by:
   ```bash
   terraform plan    # Review what will be created
   terraform apply   # Create the resources
   ```


   It is now your turn to add all the infrastructure manually created in Part 1. You should rely on this documentation [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) to configure all the needed resources.




## Extra Credit



## Resources

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Amazon API gateway Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [Speeding up your website with Amazon CloudFront](https://docs.aws.amazon.com/AmazonS3/latest/userguide/website-hosting-cloudfront-walkthrough.html)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)


## Submission

You will need to create one lab report per team. At the bare minimum, it should include:
1. Names and student number
2. Screenshots of your dynamoDB with the items
3. Screenshot of VPC endpoint
4. Screenshot of Lambda working with a test
4. Screenshot of API gateway methods
5. Screenshot of Cloudfront and data access test
6. Link to your GitHub repository with Terraform code
7. Explain key concepts learned during the lab.
8. Explain problems you ran into and how you were able to solve them.
9. Answer to the following questions:
   - What is the purpose of an Internet Gateway in a VPC, and why is it required for your EC2 instance to be reachable from the internet?
   - Why did we need to add routes to the route tables after creating the VPC peering connection? What would happen if we skipped this step?
   - Explain the difference between a public and private subnet. Why might you place an EC2 instance in a private subnet in a production environment?
   - What are two advantages of using Infrastructure as Code (Terraform) instead of manually configuring resources through the AWS Console?