# Product Inventory Infrastructure

This directory contains Terraform code to deploy the Product Inventory serverless REST API infrastructure.

## Architecture

The infrastructure includes:
- **VPC** with public subnet and Internet Gateway
- **DynamoDB** table for product inventory
- **VPC Endpoint** for DynamoDB access
- **Lambda** function for product search
- **API Gateway** REST API
- **S3** bucket for static website hosting
- **WAF** Web ACL for API protection

## Prerequisites

1. AWS Academy Learner Lab access with active session
2. Terraform 1.14 or later installed
3. AWS credentials configured in `~/.aws/credentials`
4. S3 bucket for Terraform state (created via CloudFormation)

## Setup Instructions

### 1. Configure AWS Credentials

Get your temporary credentials from AWS Academy:
1. Click **AWS Details** in AWS Academy
2. Click **Show** next to **AWS CLI**
3. Copy credentials to `~/.aws/credentials`

### 2. Update Configuration Files

**providers.tf**: Replace `<your-account-id>` with your AWS account ID in the backend configuration.

**terraform.tfvars**: Update these values:
- `vpc_cidr`: Choose a /24 CIDR that doesn't overlap with your partner's VPC
- `s3_bucket_suffix`: Use your initials and random characters for uniqueness

### 3. Update Website with API URL

The Terraform code automatically uses files from `initial_data/` directory. However, you need to update the API URL in the website:

1. Edit `initial_data/index.html`
2. Find the line: `const API_URL = 'https://rl7fds0q6d.execute-api.us-east-1.amazonaws.com/prod/products';`
3. You can either:
   - Leave it as is for the first deployment, then update it with the actual URL from Terraform outputs
   - Or comment it out and deploy first to get the URL

### 5. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### 6. Update Website with API URL

After the first deployment:
1. Copy the `api_gateway_invoke_url` from the Terraform outputs
2. Update `website/index.html` with this URL
3. Run `terraform apply` again to upload the updated website

### 7. Load Sample Data

Use the AWS Console or AWS CLI to load sample data into the DynamoDB table from `../initial_data/sample-data.json`.

## Outputs

After deployment, Terraform will output:
- `api_gateway_invoke_url`: Use this in your index.html
- `s3_website_url`: Access your application here
- `dynamodb_table_name`: DynamoDB table name
- `lambda_function_name`: Lambda function name

## Testing

1. Open the `s3_website_url` in your browser
2. Test the product search functionality
3. Try different filters (category, name, price range)

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

**Note**: Make sure to remove all objects from the S3 bucket before destroying, or the destroy will fail.

## Troubleshooting

### Lambda can't access DynamoDB
- Check VPC endpoint is created and associated with route table
- Verify Lambda has correct IAM role (LabRole)

### API Gateway returns errors
- Check Lambda function logs in CloudWatch
- Verify CORS is properly configured
- Test Lambda function directly in AWS Console

### Website not loading
- Verify S3 bucket policy allows public access
- Check static website hosting is enabled
- Ensure index.html is uploaded

### Terraform state issues
- Verify S3 backend bucket exists
- Check AWS credentials are valid and not expired
- Ensure you have permissions to access the state bucket
