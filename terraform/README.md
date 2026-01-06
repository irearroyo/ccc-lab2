# Terraform Deployment Guide

## Prerequisites

1. Install Terraform (>= 1.0)
2. Configure AWS CLI with credentials
3. Ensure you have appropriate AWS permissions

## Deployment Steps

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Review the Plan

```bash
terraform plan
```

### 3. Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted.

### 4. Get Outputs

```bash
terraform output
```

You'll see:
- `api_gateway_url` - Your API endpoint
- `website_url` - Your S3 website URL
- `dynamodb_table_name` - DynamoDB table name
- `lambda_function_name` - Lambda function name

### 5. Update Website with API URL

After deployment, you need to update the website with the actual API Gateway URL:

1. Copy the `api_gateway_url` from the output
2. Edit `website/index.html`
3. Replace `REPLACE_WITH_API_GATEWAY_URL` with your actual API URL
4. Re-apply Terraform:

```bash
terraform apply
```

### 6. Access Your Application

Open the `website_url` in your browser to test the application.

## Testing the API

```bash
# Get all products
curl "$(terraform output -raw api_gateway_url)"

# Filter by category
curl "$(terraform output -raw api_gateway_url)?category=Machinery"

# Search by name
curl "$(terraform output -raw api_gateway_url)?name=Drill"

# Price range
curl "$(terraform output -raw api_gateway_url)?minPrice=100&maxPrice=2000"
```

## Monitoring

### View CloudWatch Dashboard

```bash
aws cloudwatch get-dashboard \
  --dashboard-name $(terraform output -raw cloudwatch_dashboard_name)
```

Or visit the CloudWatch console and search for the dashboard name.

### View Lambda Logs

```bash
aws logs tail /aws/lambda/$(terraform output -raw lambda_function_name) --follow
```

### View API Gateway Logs

```bash
aws logs tail /aws/apigateway/product-inventory --follow
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

Type `yes` when prompted.

## Customization

### Change Region

Edit `variables.tf` and modify the `aws_region` default value, or:

```bash
terraform apply -var="aws_region=us-west-2"
```

### Change Project Name

```bash
terraform apply -var="project_name=my-custom-name"
```

### Add More Sample Data

Edit `main.tf` and add more `aws_dynamodb_table_item` resources following the existing pattern.

## Troubleshooting

### CORS Issues

If you encounter CORS errors:
1. Check that the API Gateway OPTIONS method is properly configured
2. Verify the Lambda function returns proper CORS headers
3. Check browser console for specific error messages

### Lambda Errors

View logs:
```bash
aws logs tail /aws/lambda/$(terraform output -raw lambda_function_name) --follow
```

### API Gateway 403 Errors

Ensure the Lambda permission is properly set for API Gateway to invoke the function.

### Website Not Loading

1. Verify S3 bucket policy allows public access
2. Check that static website hosting is enabled
3. Ensure the bucket is not blocked by public access settings

## Architecture

```
User → S3 (Static Website) → API Gateway → Lambda → DynamoDB
                                    ↓
                              CloudWatch (Logs & Metrics)
```

## Cost Estimation

With AWS Free Tier:
- DynamoDB: Free (25 GB, 25 WCU, 25 RCU)
- Lambda: Free (1M requests/month)
- API Gateway: Free for 12 months (1M requests/month)
- S3: ~$0.023/GB/month
- CloudWatch: Free tier (10 metrics, 5GB logs)

Estimated cost: $0-2/month for light usage
