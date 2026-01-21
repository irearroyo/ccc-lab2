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


### Step 6: Create API Gateway to invoke via API the Lambda function created

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
4. **Copy the Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`) then you need to add the path /products to the url to access the methods

![Enable Static Website Hosting](img/step8_1.png)

### Step 9: Create S3 Bucket for hosting the Static Website

1. Navigate to **S3 Console**
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `product-inventory-web-us-east-1-[your-initials-random]` (must be globally unique)
   - **Region**: Same as your other resources
   - **Uncheck** "Block all public access"
    Tou can check the options
□ Block public access granted through new ACLs (opcional)
□ Block public access granted through any ACLs (opcional)

![s3 access](img/step9_1.png)

   - Acknowledge the warning

4. Click **Create bucket**
5. Once created, go to Permissions from the new bucket created and add the following Bucket policy to enable to access to the website you are going to host

![s3 access policy](img/step9_2.png)
IMPORTANT: Replace s3 bucket name in YOUR-BUCKET-NAME

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


### Step 10: Enable Static Website Hosting

1. Open your bucket → **Properties** tab
![Enable Static Website Hosting](img/step10_1.png)
![Enable Static Website Hosting](img/step10_2.png)
2. Scroll to **Static website hosting** → **Edit**
3. Configure:
   - **Static website hosting**: Enable
   - **Hosting type**: Host a static website
   - **Index document**: `index.html`
4. Click **Save changes**

![Enable Static Website Hosting](img/step10_3.png)

5. **Copy the Bucket website endpoint URL, you need it to access the page later**



### Step 11: Create and Upload Static Website

Create `index.html` with the content from 'initial_data/index.html' content (IMPORTANT: replace `YOUR-API-GATEWAY-URL`with the Invoke URL from API gateway adding the name of the path you added e.g. `https://abc123.execute-api.us-east-1.amazonaws.com/prod/products`):

![replace index](img/step11_2.png)

Upload to S3:
1. Go to your S3 bucket → **Objects** tab
2. Click **Upload** → **Add files**
3. Select `index.html`
4. Click **Upload**

![Upload index](img/step11_1.png)


### Step 12: Create WAF Web ACL to protect the API

1. Navigate to **WAF & Shield Console**
2. Click **Web ACLs** → **Create web ACL**
3. Select **App category** -> API & integration services
4. Select resources to protect -> Add Resources -> Add regional resources (you will see some errors for access denied, but you can proceed)
5. Select you API gateway previously created to protect
6. Select the recommended plan for you with all the protection
![WAF](img/step12_1.png)

7. In the created WAF, click on Rules to understand what is enabled
8. Add a new rule, 
    -  Click **Add rules** → **Add managed rule groups**
    - Expand **AWS managed rule groups**
    - Enable these rule groups:
    - ✓ **Core rule set** (protects against common threats)
    - ✓ **Known bad inputs** (blocks malicious patterns)
    - ✓ **SQL database** (SQL injection protection)

**Note**: WAF will now protect your API from common attacks.

![WAF rules](img/step12_2.png)



### Step 13: Test the Application

1. Open the **Bucket website endpoint URL** in a browser (from Step 10)
2. The page should load and display all products
3. Test search filters:
   - Filter by category
   - Search by name
   - Filter by price range
   - Combine multiple filters




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
## Extra credit: Infrastructure as Code

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

Create a Cloudwatch Alarm to identify error in the Lambda and create a SNS notifiction by email

## Resources

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Amazon API gateway Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [Web hosting in Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)


## Submission

You will need to create one lab report. At the bare minimum, it should include:
1. Names and student number
2. Screenshots of your DynamoDB with the items
3. Screenshot of VPC endpoint
4. Screenshot of Lambda working with a test
5. Screenshot of API Gateway methods
6. Screenshot of S3 static website and data access test
7. Screenshot of WAF Web ACL with enabled rules
8. Link to your GitHub repository with Terraform code
9. Explain key concepts learned during the lab.
10. Explain problems you ran into and how you were able to solve them.
11. Answer to the following questions:
   - What is the purpose of a VPC Endpoint for DynamoDB, and why did we use it instead of a NAT Gateway? What are the cost and security benefits?
   - Why did we place the Lambda function inside a VPC? What are the trade-offs of running Lambda in a VPC versus outside a VPC?
   - What is the purpose of API Gateway in this architecture? Explain how it connects the S3 static website to the Lambda function and what benefits it provides.
   - Explain the purpose of AWS WAF and describe at least two types of attacks that the managed rule groups we enabled (Core rule set, Known bad inputs, SQL database) can protect against.









   